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
    """
    Przygotowuje dane testowe ze wskazanego zbioru danych.

    :param dataset_name: Nazwa zbioru danych do pobrania.
    :param config: Konfiguracja zbioru danych (np. wersja językowa).
    :param split: Część zbioru danych (np. 'test[:50]' - pierwsze 50 przykładów testowych).
    :return: Wczytany zbiór danych.
    """
    dataset = datasets.load_dataset(dataset_name, config, split=split)
    return dataset

def normalize_text(text):
    """
    Normalizuje tekst poprzez usunięcie znaków specjalnych i przekształcenie na małe litery.

    :param text: Tekst do normalizacji.
    :return: Znormalizowany tekst.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def transcribe_with_wav2vec(model_name, audio_path):
    """
    Transkrybuje audio za pomocą modelu Wav2Vec2 z Hugging Face.

    :param model_name: Nazwa modelu Wav2Vec2.
    :param audio_path: Ścieżka do pliku audio.
    :return: Ztranskrybowany tekst.
    """
    processor = Wav2Vec2Processor.from_pretrained(model_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name)
    model.eval()

    # Ładowanie pliku audio i ewentualna zmiana częstotliwości próbkowania na 16 kHz
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)

    # Przetwarzanie danych wejściowych dla modelu
    input_values = processor(waveform.squeeze().numpy(), return_tensors="pt", sampling_rate=16000).input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    return processor.batch_decode(predicted_ids)[0]

def calculate_additional_metrics(y_true, y_pred):
    """
    Oblicza dodatkowe metryki: F1, recall i accuracy.

    :param y_true: Lista prawdziwych etykiet (tekstów referencyjnych).
    :param y_pred: Lista przewidywanych etykiet (tekstów wygenerowanych).
    :return: F1, recall i accuracy.
    """
    f1 = f1_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    accuracy = accuracy_score(y_true, y_pred)
    return f1, recall, accuracy

def main():
    # Inicjalizacja usługi transkrypcji (Whisper)
    transcription_service = TranscriptionService(model_name="base")
    # Lista modeli Wav2Vec2 do porównania
    wav2vec_models = ["facebook/wav2vec2-base-960h", "jonatasgrosman/wav2vec2-large-xlsr-53-english"]

    # Przygotowanie danych testowych
    dataset = prepare_data()

    y_true = [] # Lista tekstów referencyjnych
    y_pred_whisper = [] # Lista Prediction Whisper
    y_pred_wav2vec = {model_name: [] for model_name in wav2vec_models} # Prediction Wav2Vec2

    rouge_scores_whisper = [] # Wyniki ROUGE dla Whisper
    rouge_scores_wav2vec = {model_name: [] for model_name in wav2vec_models} # Wyniki ROUGE dla Wav2Vec2

    # Iteracja po przykładach w zbiorze danych
    for i, sample in enumerate(dataset, start=1):
        try:
            print(f"Processing sample {i}/50")
            # Wczytanie pliku audio
            audio_data = BytesIO(sample["wav"]["bytes"])
            waveform, sample_rate = torchaudio.load(audio_data)

            reference_text = sample["text"] # Tekst referencyjny

            # Zapis tymczasowego pliku audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                torchaudio.save(temp_file.name, waveform, sample_rate)
                temp_path = temp_file.name

            # Transkrypcja za pomocą Whisper
            predicted_text_whisper = transcription_service.transcribe(temp_path)

            # Transkrypcje za pomocą Wav2Vec2
            predicted_text_wav2vec = {}
            for model_name in wav2vec_models:
                predicted_text_wav2vec[model_name] = transcribe_with_wav2vec(model_name, temp_path)

            os.remove(temp_path) # Usunięcie tymczasowego pliku

            # Normalizacja tekstów
            reference_text_normalized = normalize_text(reference_text)
            predicted_text_whisper_normalized = normalize_text(predicted_text_whisper)

            print(f"Reference Text (Normalized): {reference_text_normalized}")
            print(f"Whisper Predicted Text (Normalized): {predicted_text_whisper_normalized}")

            y_true.append(reference_text_normalized)
            y_pred_whisper.append(predicted_text_whisper_normalized)

            # Obliczanie ROUGE dla Whisper
            scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
            scores_whisper = scorer.score(reference_text_normalized, predicted_text_whisper_normalized)
            rouge_scores_whisper.append(scores_whisper)

            # Przetwarzanie wyników Wav2Vec2
            for model_name, pred_text in predicted_text_wav2vec.items():
                pred_text_normalized = normalize_text(pred_text)
                y_pred_wav2vec[model_name].append(pred_text_normalized)
                print(f"{model_name} Predicted Text (Normalized): {pred_text_normalized}")

                # Obliczanie ROUGE dla Wav2Vec2
                scores_wav2vec = scorer.score(reference_text_normalized, pred_text_normalized)
                rouge_scores_wav2vec[model_name].append(scores_wav2vec)

        except Exception as e:
            print(f"Error processing sample {i}/50: {e}")
            continue

    # Obliczanie średnich wyników ROUGE dla Whisper
    if rouge_scores_whisper:
        avg_rouge1 = sum(score["rouge1"].fmeasure for score in rouge_scores_whisper) / len(rouge_scores_whisper)
        avg_rouge2 = sum(score["rouge2"].fmeasure for score in rouge_scores_whisper) / len(rouge_scores_whisper)
        avg_rougeL = sum(score["rougeL"].fmeasure for score in rouge_scores_whisper) / len(rouge_scores_whisper)
        print(f"Whisper Average Rouge-1 F1: {avg_rouge1:.4f}")
        print(f"Whisper Average Rouge-2 F1: {avg_rouge2:.4f}")
        print(f"Whisper Average Rouge-L F1: {avg_rougeL:.4f}")

    # Obliczanie średnich wyników ROUGE dla Wav2Vec2
    for model_name, scores in rouge_scores_wav2vec.items():
        if scores:
            avg_rouge1 = sum(score["rouge1"].fmeasure for score in scores) / len(scores)
            avg_rouge2 = sum(score["rouge2"].fmeasure for score in scores) / len(scores)
            avg_rougeL = sum(score["rougeL"].fmeasure for score in scores) / len(scores)
            print(f"{model_name} Average Rouge-1 F1: {avg_rouge1:.4f}")
            print(f"{model_name} Average Rouge-2 F1: {avg_rouge2:.4f}")
            print(f"{model_name} Average Rouge-L F1: {avg_rougeL:.4f}")

    # Obliczanie i wyświetlanie F1, Recall i Accuracy
    y_true_normalized = [normalize_text(t) for t in y_true]

    # Wyniki dla Whisper
    whisper_f1, whisper_recall, whisper_accuracy = calculate_additional_metrics(y_true_normalized, y_pred_whisper)
    print(f"Whisper F1 Score: {whisper_f1:.4f}")
    print(f"Whisper Recall: {whisper_recall:.4f}")
    print(f"Whisper Accuracy: {whisper_accuracy:.4f}")

    # Wyniki dla każdego modelu Wav2Vec2
    for model_name, predictions in y_pred_wav2vec.items():
        model_f1, model_recall, model_accuracy = calculate_additional_metrics(y_true_normalized, predictions)
        print(f"{model_name} F1 Score: {model_f1:.4f}")
        print(f"{model_name} Recall: {model_recall:.4f}")
        print(f"{model_name} Accuracy: {model_accuracy:.4f}")

if __name__ == "__main__":
    main()
