import os
from io import BytesIO
import torchaudio
import datasets
from rouge_score import rouge_scorer
from transcription_service import TranscriptionService
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
from sklearn.metrics import f1_score, recall_score, accuracy_score
import tempfile
import re

def prepare_data(dataset_name="speechbrain/LargeScaleASR", config="small", split="test[:50]"):
    dataset = datasets.load_dataset(dataset_name, config, split=split)
    return dataset

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def transcribe_with_wav2vec(model_name, audio_path):
    """
    Transcribes audio using a Wav2Vec2 model from Hugging Face.

    :param model_name: Name of the Hugging Face model.
    :param audio_path: Path to the audio file.
    :return: Transcribed text.
    """
    processor = Wav2Vec2Processor.from_pretrained(model_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name)
    model.eval()

    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)

    input_values = processor(waveform.squeeze().numpy(), return_tensors="pt", sampling_rate=16000).input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    return processor.batch_decode(predicted_ids)[0]

def calculate_additional_metrics(y_true, y_pred):
    """
    Calculate F1-score, recall, and accuracy for the predictions.

    :param y_true: List of true labels.
    :param y_pred: List of predicted labels.
    :return: F1-score, recall, and accuracy.
    """
    f1 = f1_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    accuracy = accuracy_score(y_true, y_pred)
    return f1, recall, accuracy

def main():
    transcription_service = TranscriptionService(model_name="base")
    wav2vec_models = ["facebook/wav2vec2-base-960h", "jonatasgrosman/wav2vec2-large-xlsr-53-english"]

    dataset = prepare_data()

    y_true = []
    y_pred_whisper = []
    y_pred_wav2vec = {model_name: [] for model_name in wav2vec_models}

    rouge_scores_whisper = []
    rouge_scores_wav2vec = {model_name: [] for model_name in wav2vec_models}

    for i, sample in enumerate(dataset, start=1):
        try:
            print(f"Processing sample {i}/50")
            audio_data = BytesIO(sample["wav"]["bytes"])
            waveform, sample_rate = torchaudio.load(audio_data)

            reference_text = sample["text"]

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                torchaudio.save(temp_file.name, waveform, sample_rate)
                temp_path = temp_file.name

            # Whisper transcription
            predicted_text_whisper = transcription_service.transcribe(temp_path)

            # Wav2Vec2 transcriptions
            predicted_text_wav2vec = {}
            for model_name in wav2vec_models:
                predicted_text_wav2vec[model_name] = transcribe_with_wav2vec(model_name, temp_path)

            os.remove(temp_path)

            # Normalize reference and predicted texts
            reference_text_normalized = normalize_text(reference_text)
            predicted_text_whisper_normalized = normalize_text(predicted_text_whisper)

            print(f"Reference Text (Normalized): {reference_text_normalized}")
            print(f"Whisper Predicted Text (Normalized): {predicted_text_whisper_normalized}")

            y_true.append(reference_text_normalized)
            y_pred_whisper.append(predicted_text_whisper_normalized)

            # Calculate Whisper ROUGE
            scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
            scores_whisper = scorer.score(reference_text_normalized, predicted_text_whisper_normalized)
            rouge_scores_whisper.append(scores_whisper)

            # Process Wav2Vec2 results
            for model_name, pred_text in predicted_text_wav2vec.items():
                pred_text_normalized = normalize_text(pred_text)
                y_pred_wav2vec[model_name].append(pred_text_normalized)
                print(f"{model_name} Predicted Text (Normalized): {pred_text_normalized}")

                # Calculate Wav2Vec2 ROUGE
                scores_wav2vec = scorer.score(reference_text_normalized, pred_text_normalized)
                rouge_scores_wav2vec[model_name].append(scores_wav2vec)

        except Exception as e:
            print(f"Error processing sample {i}/50: {e}")
            continue

    # Calculate average ROUGE scores
    if rouge_scores_whisper:
        avg_rouge1 = sum(score["rouge1"].fmeasure for score in rouge_scores_whisper) / len(rouge_scores_whisper)
        avg_rouge2 = sum(score["rouge2"].fmeasure for score in rouge_scores_whisper) / len(rouge_scores_whisper)
        avg_rougeL = sum(score["rougeL"].fmeasure for score in rouge_scores_whisper) / len(rouge_scores_whisper)
        print(f"Whisper Average Rouge-1 F1: {avg_rouge1:.4f}")
        print(f"Whisper Average Rouge-2 F1: {avg_rouge2:.4f}")
        print(f"Whisper Average Rouge-L F1: {avg_rougeL:.4f}")

    for model_name, scores in rouge_scores_wav2vec.items():
        if scores:
            avg_rouge1 = sum(score["rouge1"].fmeasure for score in scores) / len(scores)
            avg_rouge2 = sum(score["rouge2"].fmeasure for score in scores) / len(scores)
            avg_rougeL = sum(score["rougeL"].fmeasure for score in scores) / len(scores)
            print(f"{model_name} Average Rouge-1 F1: {avg_rouge1:.4f}")
            print(f"{model_name} Average Rouge-2 F1: {avg_rouge2:.4f}")
            print(f"{model_name} Average Rouge-L F1: {avg_rougeL:.4f}")

    # Calculate and print F1, Recall, and Accuracy
    y_true_normalized = [normalize_text(t) for t in y_true]

    # For Whisper
    whisper_f1, whisper_recall, whisper_accuracy = calculate_additional_metrics(y_true_normalized, y_pred_whisper)
    print(f"Whisper F1 Score: {whisper_f1:.4f}")
    print(f"Whisper Recall: {whisper_recall:.4f}")
    print(f"Whisper Accuracy: {whisper_accuracy:.4f}")

    # For each Wav2Vec2 model
    for model_name, predictions in y_pred_wav2vec.items():
        model_f1, model_recall, model_accuracy = calculate_additional_metrics(y_true_normalized, predictions)
        print(f"{model_name} F1 Score: {model_f1:.4f}")
        print(f"{model_name} Recall: {model_recall:.4f}")
        print(f"{model_name} Accuracy: {model_accuracy:.4f}")

if __name__ == "__main__":
    main()
