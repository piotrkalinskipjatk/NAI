from fastapi import FastAPI, UploadFile, File, HTTPException
from summarizer_service import SummarizerService
from transcription_service import TranscriptionService
from pathlib import Path

app = FastAPI()
transcription_service = TranscriptionService()
summarizer_service = SummarizerService()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    """
    Endpoint obsługujący transkrypcję i podsumowanie pliku MP4.

    :param file: Plik MP4 przesłany przez użytkownika.
    :return: Podsumowanie tekstu z transkrypcji.
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

        Path(temp_video_path).unlink()

        summary = summarizer_service.summarize(temp_transcription_path)

        Path(temp_transcription_path).unlink()

        return {"summary": summary}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")
