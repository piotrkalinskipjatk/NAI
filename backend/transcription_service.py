import whisper
from pathlib import Path

class TranscriptionService:
    def __init__(self, model_name: str = "base"):
        """
        Inicjalizuje usługę transkrypcji, ładując model Whisper.

        :param model_name: Nazwa wariantu modelu Whisper (np. "tiny", "base", "small", "medium", "large").
        """
        # Ładowanie modelu Whisper na urządzenie CUDA (GPU), jeśli jest dostępne
        self.model = whisper.load_model(model_name, device="cuda")

    def transcribe(self, file_path: str) -> str:
        """
        Przeprowadza transkrypcję na podstawie podanego pliku MP4.

        :param file_path: Ścieżka do pliku wideo.
        :return: Tekst transkrypcji.
        """
        # Sprawdzenie, czy plik istnieje, aby uniknąć błędów przy próbie jego przetwarzania
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Plik {file_path} nie istnieje.")

        try:
            # Przeprowadzenie transkrypcji za pomocą modelu Whisper
            # Metoda `transcribe` zwraca słownik z różnymi danymi, w tym pełnym tekstem transkrypcji
            result = self.model.transcribe(str(Path(file_path).resolve()))
            return result["text"] # Zwrócenie samego tekstu transkrypcji
        except Exception as e:
            # Jeśli wystąpi błąd, jest on propagowany wyżej
            raise
