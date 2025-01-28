import os
from yt_dlp import YoutubeDL

OUTPUT_VIDEO_DIR = "videos"
LINKS_FILE = "video_links.txt"

# Tworzenie katalogu na filmy, jeśli nie istnieje
os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)


def download_video(video_url, output_path):
    """
    Pobiera film z YouTube na podstawie podanego URL i zapisuje go w określonym katalogu.

    :param video_url: URL filmu YouTube.
    :param output_path: Ścieżka do katalogu, w którym film ma zostać zapisany.
    """
    # Opcje konfiguracji dla yt_dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', # Pobranie najlepszego dostępnego wideo i audio
        'merge_output_format': 'mp4', # Scalanie wideo i audio w plik MP4
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'), # Nazwa pliku zgodna z ID filmu
        'quiet': False, # Wyświetlanie szczegółowych informacji o pobieraniu
    }

    # Pobieranie filmu za pomocą yt_dlp
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def read_links_from_file(file_path):
    """
    Wczytuje listę linków z pliku tekstowego.

    :param file_path: Ścieżka do pliku zawierającego linki.
    :return: Lista linków wczytanych z pliku.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()] # Usunięcie pustych linii
    return links

# Próba wczytania linków z pliku
try:
    video_links = read_links_from_file(LINKS_FILE)
except FileNotFoundError:
    print(f"Plik {LINKS_FILE} nie został znaleziony.")
    video_links = [] # Pusta lista, jeśli plik nie istnieje

# Pobieranie maksymalnie 10 filmów z listy
for i, video_url in enumerate(video_links):
    if i >= 10:
        break

    print(f"Pobieram film: {video_url}")

    try:
        # Pobranie pojedynczego filmu
        download_video(video_url, OUTPUT_VIDEO_DIR)
    except Exception as e:
        # Obsługa błędów podczas pobierania
        print(f"Nie udało się pobrać filmu: {video_url}. Błąd: {e}")
        continue

print("Proces zakończony.")
