from transformers import pipeline
from pathlib import Path
from torch import cuda

class SummarizerService:
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        """
        Inicjalizuje usługę podsumowań, ładując model.

        :param model_name: Nazwa modelu do podsumowywania tekstów, pobieranego z biblioteki Transformers.
        """
        # Sprawdzanie, czy dostępne jest GPU. Jeśli tak, użyj urządzenia CUDA (device=0), w przeciwnym razie użyj CPU (device=-1)
        device = 0 if cuda.is_available() else -1
        # Inicjalizacja pipeline dla zadania podsumowania tekstów
        self.summarizer = pipeline("summarization", model=model_name, device=device)
        # Definicja promptu jako wprowadzenia do tekstu, który będzie poddany podsumowaniu
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
        # Sprawdzanie, czy plik istnieje, aby uniknąć błędów podczas odczytu
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Plik {file_path} nie istnieje.")

        # Otwieranie i wczytywanie zawartości pliku tekstowego
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            # Dodanie promptu do treści tekstu i ograniczenie długości do 1024 znaków
            full_text = self.prompt + " " + text
            full_text = full_text[:1024]

        # Generowanie podsumowania za pomocą modelu
        # Parametry:
        # - max_length: Maksymalna długość podsumowania
        # - min_length: Minimalna długość podsumowania
        # - do_sample=False: Deterministyczne generowanie zamiast losowego próbkowania
        result = self.summarizer(full_text, max_length=120, min_length=50, do_sample=False)

        # Zwrócenie wygenerowanego podsumowania (pierwszy wynik)
        return result[0]['summary_text']