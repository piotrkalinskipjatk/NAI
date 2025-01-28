from diffusers import DiffusionPipeline
from pathlib import Path
import torch

class ImageService:
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        """
        Inicjalizuje usługę generowania obrazów, ładując model.

        :param model_id: Identyfikator modelu z Hugging Face Hub, który ma być użyty do generowania obrazów.
        """

        # Sprawdzanie dostępności GPU (CUDA) i ustawianie urządzenia
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Ładowanie modelu DiffusionPipeline z Hugging Face
        self.pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,  # Użycie 16-bitowej precyzji dla oszczędności pamięci
            use_safetensors=True,       # Włączenie bezpieczniejszego formatu zapisu modelu
            variant="fp16"              # Wariant modelu zoptymalizowany pod kątem GPU
        )
        # Przeniesienie modelu na odpowiednie urządzenie (CPU lub GPU)
        self.pipe = self.pipe.to(self.device)

    def generate_image(self, prompt: str, output_path: str) -> str:
        """
        Generuje obraz na podstawie podanego promptu i zapisuje go do pliku.

        :param prompt: Tekst opisujący obraz do wygenerowania.
        :param output_path: Ścieżka do zapisu wygenerowanego obrazu.
        :return: Ścieżka do wygenerowanego obrazu.
        """
        try:
            # Optymalizacja pamięci - sekwencyjne przenoszenie elementów modelu między CPU a GPU
            self.pipe.enable_sequential_cpu_offload()

            # Generowanie obrazu na podstawie podanego promptu
            image = self.pipe(prompt=prompt).images[0]
            # Przygotowanie ścieżki do zapisu obrazu
            image_path = Path(output_path)
            image_path.parent.mkdir(parents=True, exist_ok=True) # Tworzenie katalogów, jeśli nie istnieją
            # Zapis wygenerowanego obrazu
            image.save(image_path)
            return str(image_path)
        except Exception as e:
            # Obsługa błędów
            raise RuntimeError(f"Error generating image: {e}")
