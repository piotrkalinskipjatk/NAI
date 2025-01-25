import whisper

model = whisper.load_model("base")
result = model.transcribe("videos/35Pdoyi6ZoQ.mp4")

with open("transcryption.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])
