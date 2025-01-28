from diffusers import DiffusionPipeline
from pathlib import Path
import torch

class ImageService:
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        """
        Inicjalizuje usługę generowania obrazów, ładując model.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )
        self.pipe = self.pipe.to(self.device)

    def generate_image(self, prompt: str, output_path: str) -> str:
        """
        Generuje obraz na podstawie podanego promptu i zapisuje go do pliku.

        :param prompt: Tekst opisujący obraz do wygenerowania.
        :param output_path: Ścieżka do zapisu wygenerowanego obrazu.
        :return: Ścieżka do wygenerowanego obrazu.
        """
        try:
            self.pipe.enable_sequential_cpu_offload()

            image = self.pipe(prompt=prompt).images[0]
            image_path = Path(output_path)
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(image_path)
            return str(image_path)
        except Exception as e:
            raise RuntimeError(f"Error generating image: {e}")
