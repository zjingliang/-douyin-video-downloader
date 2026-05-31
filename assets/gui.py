import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import download_douyin_videos


class DouyinDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Douyin Video Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.create_widgets()
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Info.TLabel", font=("Arial", 10))
        style.configure("Download.TButton", font=("Arial", 11))

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Douyin Video Downloader", style="Title.TLabel")
        title_label.pack(pady=(0, 15))

        url_frame = ttk.LabelFrame(main_frame, text="Douyin Share URLs (one per line)", padding="10")
        url_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.url_text = scrolledtext.ScrolledText(
            url_frame,
            height=10,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.url_text.pack(fill=tk.BOTH, expand=True)
        self.url_text.insert("1.0", "Please enter Douyin share URLs, one per line:\nExample:\nhttps://v.douyin.com/xxxxxx/\nhttps://v.douyin.com/yyyyyy/")
        self.url_text.bind("<FocusIn>", self.on_url_focus_in)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.download_btn = ttk.Button(
            button_frame,
            text="Start Download",
            style="Download.TButton",
            command=self.start_download
        )
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear URLs",
            command=self.clear_urls
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.open_folder_btn = ttk.Button(
            button_frame,
            text="Open Output Folder",
            command=self.open_save_folder
        )
        self.open_folder_btn.pack(side=tk.LEFT)

        log_frame = ttk.LabelFrame(main_frame, text="Download Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=("Arial", 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            style="Info.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)

        self.progress_label = ttk.Label(
            status_frame,
            text="",
            style="Info.TLabel"
        )
        self.progress_label.pack(side=tk.RIGHT)

    def on_url_focus_in(self, event):
        placeholder = "Please enter Douyin share URLs, one per line:\nExample:\nhttps://v.douyin.com/xxxxxx/\nhttps://v.douyin.com/yyyyyy/"
        if self.url_text.get("1.0", "1.end") == placeholder:
            self.url_text.delete("1.0", tk.END)

    def clear_urls(self):
        self.url_text.delete("1.0", tk.END)

    def open_save_folder(self):
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        if not os.path.exists(output_path):
            output_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.startfile(output_path)

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def update_status(self, status):
        self.status_label.config(text=status)
        self.root.update_idletasks()

    def update_progress(self, current, total):
        if total > 0:
            self.progress_label.config(text=f"Progress: {current}/{total}")
        else:
            self.progress_label.config(text="")
        self.root.update_idletasks()

    def start_download(self):
        urls_text = self.url_text.get("1.0", tk.END).strip()

        placeholder = "Please enter Douyin share URLs, one per line:\nExample:\nhttps://v.douyin.com/xxxxxx/\nhttps://v.douyin.com/yyyyyy/"
        if not urls_text or urls_text == placeholder:
            messagebox.showwarning("Warning", "Please enter at least one Douyin URL!")
            return

        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

        if not urls:
            messagebox.showwarning("Warning", "Please enter at least one Douyin URL!")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.log_message(f"Starting download of {len(urls)} item(s)...")
        self.update_status("Downloading...")

        thread = threading.Thread(target=self.download_videos, args=(urls,))
        thread.daemon = True
        thread.start()

    def download_videos(self, urls):
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, "output")

            results = download_douyin_videos(urls, output_dir=output_dir)

            success_count = sum(1 for r in results if r["success"])
            fail_count = len(results) - success_count

            self.log_message(f"\nDownload Summary:")
            self.log_message(f"Success: {success_count}")
            self.log_message(f"Failed: {fail_count}")

            for i, result in enumerate(results, 1):
                status = "OK" if result["success"] else "FAIL"
                self.log_message(f"[{status}] {result.get('title', result['url'])} - {result['message']}")

            self.update_status("Download Complete")
            messagebox.showinfo("Complete", f"Download complete!\nSuccess: {success_count}\nFailed: {fail_count}")

        except Exception as e:
            self.log_message(f"\nError during download: {str(e)}")
            self.update_status("Download Failed")
            messagebox.showerror("Error", f"Download failed:\n{str(e)}")

        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.update_progress(0, 0)


def main():
    root = tk.Tk()
    app = DouyinDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
