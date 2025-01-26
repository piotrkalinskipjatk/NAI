import whisper
from pathlib import Path


class TranscriptionService:
    def __init__(self, model_name: str = "base"):
        """
        Inicjalizuje usługę transkrypcji, ładując model Whisper.
        """
        self.model = whisper.load_model(model_name)

    def transcribe(self, file_path: str) -> str:
        """
        Przeprowadza transkrypcję na podstawie podanego pliku MP4.

        :param file_path: Ścieżka do pliku wideo.
        :return: Tekst transkrypcji.
        """
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Plik {file_path} nie istnieje.")

        result = self.model.transcribe(file_path)
        return result["text"]
