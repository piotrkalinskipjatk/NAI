import os
from io import BytesIO
import torchaudio
import datasets
from rouge_score import rouge_scorer
from transcription_service import TranscriptionService
import tempfile
import re


def prepare_data(dataset_name="speechbrain/LargeScaleASR", config="small", split="test[:50]"):
    dataset = datasets.load_dataset(dataset_name, config, split=split)
    return dataset

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def main():
    transcription_service = TranscriptionService(model_name="base")

    dataset = prepare_data()

    y_true = []
    y_pred = []
    rouge_scores = []

    for i, sample in enumerate(dataset, start=1):
        try:
            print(f"Processing sample {i}/50")
            audio_data = BytesIO(sample["wav"]["bytes"])
            waveform, sample_rate = torchaudio.load(audio_data)

            reference_text = sample["text"]

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                torchaudio.save(temp_file.name, waveform, sample_rate)
                temp_path = temp_file.name

            predicted_text = transcription_service.transcribe(temp_path)

            os.remove(temp_path)

            reference_text_normalized = normalize_text(reference_text)
            predicted_text_normalized = normalize_text(predicted_text)

            print(f"Reference Text (Normalized): {reference_text_normalized}")
            print(f"Predicted Text (Normalized): {predicted_text_normalized}")

            y_true.append(reference_text_normalized)
            y_pred.append(predicted_text_normalized)

            scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
            scores = scorer.score(reference_text_normalized, predicted_text_normalized)
            rouge_scores.append(scores)

        except Exception as e:
            print(f"Error processing sample {i}/50: {e}")
            continue

    if rouge_scores:
        avg_rouge1 = sum(score["rouge1"].fmeasure for score in rouge_scores) / len(rouge_scores)
        avg_rouge2 = sum(score["rouge2"].fmeasure for score in rouge_scores) / len(rouge_scores)
        avg_rougeL = sum(score["rougeL"].fmeasure for score in rouge_scores) / len(rouge_scores)
        print(f"Average Rouge-1 F1: {avg_rouge1:.4f}")
        print(f"Average Rouge-2 F1: {avg_rouge2:.4f}")
        print(f"Average Rouge-L F1: {avg_rougeL:.4f}")
    else:
        print("No Rouge scores calculated.")


if __name__ == "__main__":
    main()