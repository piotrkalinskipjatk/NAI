from fastapi import FastAPI, UploadFile, File, HTTPException
from summarizer_service import SummarizerService
from transcription_service import TranscriptionService
from pathlib import Path
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware
from diffusers import StableDiffusionPipeline
import torch
app = FastAPI()
transcription_service = TranscriptionService()
summarizer_service = SummarizerService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ładowanie modelu Stable Diffusion v1.5 z Hugging Face
model_id = "sd-legacy/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

class FileMetadata(BaseModel):
    style: str
    color: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}



@app.post("/generate/")
async def process_file(
    file: UploadFile = File(...),
    style: str = Form(...),
    color: str = Form(...)
):
    """
    Endpoint obsługujący przetwarzanie pliku MP4, generowanie transkrypcji i obrazu
    przy użyciu modelu FLUX.
    """
    try:
        print(f"Received file: {file.filename}")
        print(f"Style: {style}")
        print(f"Color: {color}")

        # Przechowywanie przesłanego pliku
        sanitized_filename = "".join(c for c in Path(file.filename).stem if c.isalnum()) + ".mp4"
        temp_video_path = str(Path(f"temp_{sanitized_filename}").resolve())
        temp_transcription_path = str(Path(f"temp_{Path(sanitized_filename).stem}.txt").resolve())

        print(f"Temporary video path: {temp_video_path}")

        with open(temp_video_path, "wb") as buffer:
            buffer.write(await file.read())

        print("File saved successfully.")

        if not Path(temp_video_path).is_file():
            raise HTTPException(status_code=500, detail="Temporary video file was not created.")

        # Transkrypcja wideo
        transcription = transcription_service.transcribe(temp_video_path)
        print("Transcription completed.")

        with open(temp_transcription_path, "w", encoding="utf-8") as text_file:
            text_file.write(transcription)

        # Generowanie podsumowania
        summary = summarizer_service.summarize(temp_transcription_path)
        print(f"Summary: {summary}")

        # Generowanie obrazu przy użyciu FLUX
        prompt = f"{summary} in Style: {style}, in Color: {color}."
        image_path = Path(f"images/generated_image.jpg").resolve()
        image_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Prompt: {prompt}")

        # Generowanie obrazu
        image = pipe(prompt).images[0]
        image.save(image_path)

        print(f"Image saved at {image_path}")

        # Usuwanie tymczasowych plików
        Path(temp_video_path).unlink()
        Path(temp_transcription_path).unlink()

        # Zwracanie wygenerowanego obrazu
        return FileResponse(
            path=f"{image_path}",
            media_type="image/jpeg",
            filename="generated_image.jpg"
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")