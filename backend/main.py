from fastapi import FastAPI, UploadFile, File, HTTPException
from transcription_service import TranscriptionService
from pathlib import Path

app = FastAPI()
transcription_service = TranscriptionService()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    """
    Endpoint do transkrypcji pliku wideo MP4.

    :param file: Plik MP4 przesłany przez użytkownika.
    :return: Transkrypcja pliku wideo.
    """
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        transcription = transcription_service.transcribe(file_path)

        Path(file_path).unlink()

        return {"transcription": transcription}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")
