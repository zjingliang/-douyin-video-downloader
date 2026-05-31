import requests
import re
import json
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy import concatenate_videoclips
from moviepy.audio.io.AudioFileClip import AudioFileClip


USER_AGENT = "Mozilla/5.0 (Linux; Android 11; 2112123AC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5307 MMWEBSDK/20230805 MMWEBID/3181 MicroMessenger/8.0.42.2460(0x28002A61) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"


def get_video_info(share_url):
    headers = {
        "referer": "https://www.douyin.com/",
        "user-agent": USER_AGENT
    }

    match = re.search(r'https://v\.douyin\.com/[a-zA-Z0-9_-]+/?', share_url)
    if not match:
        raise ValueError(f"Invalid Douyin URL format: {share_url}")
    video_url = match.group()

    response = requests.get(video_url, headers=headers, timeout=30)
    response.raise_for_status()
    response_text = response.text

    data = re.findall(r'window\._ROUTER_DATA = (.*?)</script>', response_text)
    if not data:
        raise ValueError("Unable to find page data in response")
    json_data = json.loads(data[0])

    loader_data = json_data["loaderData"]
    page_key = None

    if "video_(id)/page" in loader_data:
        page_key = "video_(id)/page"
    elif "note_(id)/page" in loader_data:
        page_key = "note_(id)/page"
    else:
        raise ValueError(f"Unable to find page data, available keys: {list(loader_data.keys())}")

    video_data = loader_data[page_key]["videoInfoRes"]["item_list"]

    video_title = video_data[0]["desc"]
    video_title = re.sub(r'[\\/:*?"<>|\s]', '', video_title)

    video_info = video_data[0].get("video", {})
    media_url = None
    media_type = "video"
    image_urls = []

    if "images" in video_data[0] and video_data[0]["images"]:
        for img in video_data[0]["images"]:
            if "url_list" in img and img["url_list"]:
                image_urls.append(img["url_list"][0])

    if "play_addr" in video_info:
        play_addr = video_info["play_addr"]
        if "uri" in play_addr and play_addr["uri"].endswith('.mp3'):
            media_url = play_addr["uri"]
            media_type = "audio"
        elif "url_list" in play_addr:
            for url in play_addr["url_list"]:
                if url:
                    if 'playwm' in url:
                        media_url = url.replace('playwm', 'play')
                        break
                    elif '.mp4' in url.lower() and '.mp3' not in url.lower():
                        media_url = url
                        break
                    elif '.mp3' in url.lower():
                        media_url = url
                        media_type = "audio"
                        break

    if not media_url and "download_addr" in video_info and "url_list" in video_info["download_addr"]:
        for url in video_info["download_addr"]["url_list"]:
            if url:
                if '.mp4' in url.lower() and '.mp3' not in url.lower():
                    media_url = url
                    break
                elif '.mp3' in url.lower():
                    media_url = url
                    media_type = "audio"
                    break

    if not media_url and "play_addr" in video_info and "url_list" in video_info["play_addr"]:
        media_url = video_info["play_addr"]["url_list"][0]
        if media_url and '.mp3' in media_url.lower():
            media_type = "audio"

    if not media_url:
        raise ValueError("Unable to find media playback URL")

    return video_title, media_url, media_type, image_urls


def download_file(url, save_path):
    headers = {
        "referer": "https://www.douyin.com/",
        "user-agent": USER_AGENT
    }

    response = requests.get(url, headers=headers, stream=True, timeout=60)
    response.raise_for_status()

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)

    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def extract_audio(video_path, audio_path=None):
    if audio_path is None:
        audio_path = os.path.splitext(video_path)[0] + ".mp3"

    with VideoFileClip(video_path) as clip:
        clip.audio.write_audiofile(audio_path)

    return audio_path


def images_to_video(image_paths, audio_path, output_path, fps=1):
    clips = []
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration

    if len(image_paths) == 0:
        raise ValueError("No images available for video synthesis")

    duration_per_image = audio_duration / len(image_paths)

    for img_path in image_paths:
        clip = ImageClip(img_path, duration=duration_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips)
    video = video.with_audio(audio_clip)
    video.write_videofile(output_path, fps=fps, logger=None)


def download_douyin_videos(urls, convert_image_to_video=True, output_dir='./output'):
    video_dir = os.path.join(output_dir, 'videos')
    audio_dir = os.path.join(output_dir, 'audio')
    image_dir = os.path.join(output_dir, 'images')

    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    results = []

    for idx, url in enumerate(urls, 1):
        result = {"url": url, "success": False, "message": ""}
        try:
            video_title, media_url, media_type, image_urls = get_video_info(url)
            result["title"] = video_title
            result["type"] = media_type

            if media_type == "audio":
                audio_path = os.path.join(audio_dir, f"{video_title}.mp3")
                download_file(media_url, audio_path)
                result["audio_path"] = audio_path

                if image_urls and convert_image_to_video:
                    downloaded_images = []
                    for i, img_url in enumerate(image_urls, 1):
                        img_path = os.path.join(image_dir, f"{video_title}_{i}.jpg")
                        download_file(img_url, img_path)
                        downloaded_images.append(img_path)

                    video_path = os.path.join(video_dir, f"{video_title}.mp4")
                    images_to_video(downloaded_images, audio_path, video_path)
                    result["video_path"] = video_path

                result["success"] = True
                result["message"] = "Audio/image content downloaded successfully"
            else:
                video_path = os.path.join(video_dir, f"{video_title}.mp4")
                audio_path = os.path.join(audio_dir, f"{video_title}.mp3")

                download_file(media_url, video_path)
                result["video_path"] = video_path

                try:
                    extract_audio(video_path, audio_path)
                    result["audio_path"] = audio_path
                except Exception as audio_err:
                    result["audio_message"] = f"Audio extraction skipped: {str(audio_err)}"

                result["success"] = True
                result["message"] = "Video downloaded successfully"

        except Exception as e:
            result["message"] = str(e)

        results.append(result)

    return results
