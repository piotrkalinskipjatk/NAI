from transformers import pipeline
from pathlib import Path
from torch import cuda

class SummarizerService:
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        """
        Inicjalizuje usługę podsumowań, ładując model.
        """
        device = 0 if cuda.is_available() else -1
        self.summarizer = pipeline("summarization", model=model_name, device=device)
        self.prompt = (
            "Create a concise and engaging summary that captures the essential features and visual "
            "elements of the topic. Describe its main attributes in a way that can be visually "
            "interpreted for image creation. This summary should be adaptable for YouTube video covers."
        )

    def summarize(self, file_path: str) -> str:
        """
        Tworzy podsumowanie na podstawie zawartości pliku tekstowego.

        :param file_path: Ścieżka do pliku tekstowego.
        :return: Tekst podsumowania.
        """
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Plik {file_path} nie istnieje.")

        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            full_text = self.prompt + " " + text
            full_text = full_text[:1024]

        result = self.summarizer(full_text, max_length=120, min_length=50, do_sample=False)
        return result[0]['summary_text']