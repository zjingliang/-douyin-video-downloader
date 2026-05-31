# Douyin Video Downloader

A Python-based tool for downloading videos and audio from Douyin (TikTok China).

## Features

- Download videos from Douyin share URLs
- Extract audio from downloaded videos
- Support for image+audio content (synthesize into video)
- User-friendly GUI interface
- Batch download support
- Watermark-free video download

## Requirements

- Python 3.8+
- requests
- moviepy
- tkinter (usually included with Python)

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install requests moviepy
```

## Usage

### GUI Mode

```bash
python main.py
```

Enter Douyin share URLs (one per line) and click "Start Download".

### Command Line Mode

```python
from core import download_douyin_videos

urls = [
    "https://v.douyin.com/xxxxxx/",
    "https://v.douyin.com/yyyyyy/"
]

results = download_douyin_videos(urls, output_dir="./output")
```

## Project Structure

```
douyin-video-downloader/
├── core/               # Core download functionality
│   └── __init__.py
├── assets/            # GUI and resources
│   ├── gui.py
│   └── __init__.py
├── output/            # Downloaded files directory
│   ├── videos/
│   ├── audio/
│   └── images/
├── main.py            # Entry point
├── README.md
└── LICENSE
```

## Disclaimer

**IMPORTANT: This software is provided for educational and personal use only.**

- This tool is designed to understand how web scraping and video processing work technically
- Please respect copyright and intellectual property rights
- Do not use this tool to download content that you do not have the right to download
- Commercial use or redistribution of downloaded content may violate laws and regulations
- The author(s) assume no liability for any misuse of this software

## Legal Notice

By using this software, you agree to:

1. Only use it for legal purposes
2. Respect the terms of service of Douyin
3. Not use this tool to infringe on copyright or other intellectual property rights
4. Remove any downloaded content upon request if requested by the content creator

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
