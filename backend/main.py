from fastapi import FastAPI, UploadFile, File, HTTPException
from summarizer_service import SummarizerService
from transcription_service import TranscriptionService
from pathlib import Path
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware



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
    Endpoint obsługujący przetwarzanie pliku MP4 i dodatkowe pola style i color,
    zwracający obraz z folderu /images.

    :param file: Plik MP4 przesłany przez użytkownika.
    :param style: Styl używany do generowania obrazu.
    :param color: Kolor używany do generowania obrazu.
    :return: Ścieżka do obrazu lub obraz do pobrania.
    """
    try:
        sanitized_filename = "".join(c for c in Path(file.filename).stem if c.isalnum()) + ".mp4"
        temp_video_path = str(Path(f"temp_{sanitized_filename}").resolve())
        temp_transcription_path = str(Path(f"temp_{Path(sanitized_filename).stem}.txt").resolve())

        with open(temp_video_path, "wb") as buffer:
            buffer.write(await file.read())

        if not Path(temp_video_path).is_file():
            raise HTTPException(status_code=500, detail="Temporary video file was not created.")

        transcription = transcription_service.transcribe(temp_video_path)

        with open(temp_transcription_path, "w", encoding="utf-8") as text_file:
            text_file.write(transcription)


        image_name = "generated_image.jpg"
        image_path = Path(f"images/{image_name}").resolve()

        Path(temp_video_path).unlink()
        Path(temp_transcription_path).unlink()

        if not image_path.is_file():
            raise HTTPException(status_code=500, detail="Generated image was not found.")

        return FileResponse(
            path=image_path,
            media_type="image/jpeg",
            filename=image_name
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")

