import os
from yt_dlp import YoutubeDL

OUTPUT_VIDEO_DIR = "videos"
LINKS_FILE = "video_links.txt"

os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)


def download_video(video_url, output_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'quiet': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def read_links_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]
    return links


try:
    video_links = read_links_from_file(LINKS_FILE)
except FileNotFoundError:
    print(f"Plik {LINKS_FILE} nie został znaleziony.")
    video_links = []

for i, video_url in enumerate(video_links):
    if i >= 10:
        break

    print(f"Pobieram film: {video_url}")

    try:
        download_video(video_url, OUTPUT_VIDEO_DIR)
    except Exception as e:
        print(f"Nie udało się pobrać filmu: {video_url}. Błąd: {e}")
        continue

print("Proces zakończony.")
