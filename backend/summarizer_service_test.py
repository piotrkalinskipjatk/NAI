from transformers import pipeline
from datasets import load_dataset
from rouge_score import rouge_scorer

# Wczytanie zbioru danych CNN/DailyMail (50 próbek z podziału testowego)
dataset = load_dataset('cnn_dailymail', '3.0.0', split='test[:50]')

# Definicja modeli do testowania
models = {
    "BART": "facebook/bart-large-cnn", # Model BART dużej skali
    "DistilBART": "sshleifer/distilbart-cnn-12-6", # Szybszy i lżejszy model DistilBART
}

# Inicjalizacja pipeline'ów dla każdego modelu (tworzenie obiektów do podsumowywania)
summarizers = {name: pipeline("summarization", model=model_name) for name, model_name in models.items()}

def generate_summary(summarizer, input_text):
    """
    Generuje podsumowanie za pomocą określonego modelu NLP.

    :param summarizer: Pipeline modelu do podsumowywania tekstu.
    :param input_text: Tekst do podsumowania.
    :return: Wygenerowane podsumowanie w formie tekstu.
    """
    # Ograniczenie wejściowego tekstu do maksymalnie 512 słów (model nie obsługuje dłuższych tekstów)
    if len(input_text.split()) > 512:
        input_text = ' '.join(input_text.split()[:512])

    # Generowanie podsumowania z określonymi parametrami długości
    summary = summarizer(input_text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def calculate_rouge_scores(reference, generated):
    """
    Oblicza metryki ROUGE do oceny jakości podsumowań tekstu.

    :param reference: Referencyjne (oczekiwane) podsumowanie tekstu.
    :param generated: Wygenerowane podsumowanie tekstu.
    :return: Słownik zawierający wyniki ROUGE.
    """
    # Inicjalizacja obiektu do obliczania metryk ROUGE (z uwzględnieniem stemmingu[usuwa przyrostki,aby poprawia matching])
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    # Obliczenie wyników ROUGE
    scores = scorer.score(reference, generated)
    return scores

# Iteracja po artykułach w zbiorze danych
for article in dataset:
    reference = article['highlights'] # Referencyjne podsumowanie artykułu
    for name, summarizer in summarizers.items():
        # Generowanie podsumowania za pomocą określonego modelu
        generated_summary = generate_summary(summarizer, article['article'])
        # Obliczanie wyników ROUGE dla wygenerowanego podsumowania
        rouge_scores = calculate_rouge_scores(reference, generated_summary)
        # Wyświetlanie wyników dla każdego modelu
        print(f"Model: {name}")
        print("ROUGE Scores:", rouge_scores)
        print("-" * 80)
