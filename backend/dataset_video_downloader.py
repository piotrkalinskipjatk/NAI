import os
from datasets import load_dataset
from yt_dlp import YoutubeDL

OUTPUT_VIDEO_DIR = "videos"
OUTPUT_TRANSCRIPTION_DIR = "transcriptions"

# Tworzenie katalogów, jeśli nie istnieją
os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)
os.makedirs(OUTPUT_TRANSCRIPTION_DIR, exist_ok=True)

def download_video(video_url, output_path):
    """
    Pobiera film z YouTube na podstawie podanego URL i zapisuje go w określonym katalogu.
    :param video_url: Adres URL filmu YouTube.
    :param output_path: Ścieżka do katalogu, w którym film ma zostać zapisany.
    """
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'quiet': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

# Pobranie zbioru danych zawierającego transkrypcje wideo
dataset = load_dataset('jamescalam/youtube-transcriptions', split='train')

# Przechowywanie unikalnych filmów i ich transkrypcji
unique_videos = {}
for record in dataset:
    video_id = record['video_id']
    if video_id not in unique_videos:
        unique_videos[video_id] = {
            "url": record['url'],
            "title": record['title'],
            "transcriptions": []
        }
    unique_videos[video_id]["transcriptions"].append(record['text'])

# Pobranie maksymalnie 10 filmów z transkrypcjami
for i, (video_id, video_data) in enumerate(unique_videos.items()):
    if i >= 10:
        break
    video_url = video_data["url"]
    title = video_data["title"]
    transcription_text = "\n".join(video_data["transcriptions"])

    print(f"Pobieram film: {title} (ID: {video_id})")

    try:
        download_video(video_url, OUTPUT_VIDEO_DIR)
    except Exception as e:
        print(f"Nie udało się pobrać filmu {video_id}: {e}")
        continue

    transcription_path = os.path.join(OUTPUT_TRANSCRIPTION_DIR, f"{video_id}.txt")
    with open(transcription_path, 'w', encoding='utf-8') as f:
        f.write(transcription_text)

    print(f"Zapisano transkrypcję do {transcription_path}")

print("Proces zakończony.")
