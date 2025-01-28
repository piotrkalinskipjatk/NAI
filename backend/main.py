from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from summarizer_service import SummarizerService
from transcription_service import TranscriptionService
from image_service import ImageService
from pathlib import Path
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
transcription_service = TranscriptionService()
summarizer_service = SummarizerService()
image_service = ImageService()

# Middleware z konfiguracją CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileMetadata(BaseModel):
    style: str
    color: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/generate/")
async def process_file(
    file: UploadFile = File(...),
    style: str = Form(...),
    color: str = Form(...)
):
    """
    Endpoint obsługujący przetwarzanie pliku MP4 i dodatkowe pola style i color,
    zwracający wygenerowany obraz z folderu /images.

    :param file: Plik MP4 przesłany przez użytkownika.
    :param style: Styl używany do generowania obrazu.
    :param color: Kolor używany do generowania obrazu.
    :return: Ścieżka do obrazu lub obraz do pobrania.
    """
    try:
        # Zapisanie pliku wideo
        sanitized_filename = "".join(c for c in Path(file.filename).stem if c.isalnum()) + ".mp4"
        temp_video_path = str(Path(f"temp_{sanitized_filename}").resolve())
        temp_transcription_path = str(Path(f"temp_{Path(sanitized_filename).stem}.txt").resolve())

        with open(temp_video_path, "wb") as buffer:
            buffer.write(await file.read())

        # Transkrypcja
        transcription = transcription_service.transcribe(temp_video_path)
        with open(temp_transcription_path, "w", encoding="utf-8") as text_file:
            text_file.write(transcription)

        # Podsumowanie
        summary = summarizer_service.summarize(temp_transcription_path)

        # Generowanie obrazu
        prompt = f"{summary} in Style: {style}, in Color: {color}."
        image_path = image_service.generate_image(prompt, "images/generated_image.jpg")

        # Usuwanie plików tymczasowych
        Path(temp_video_path).unlink()
        Path(temp_transcription_path).unlink()

        # Zwracanie wygenerowanego obrazu
        return FileResponse(
            path=image_path,
            media_type="image/jpeg",
            filename="generated_image.jpg"
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")