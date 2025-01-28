from transformers import pipeline
from datasets import load_dataset
from rouge_score import rouge_scorer

dataset = load_dataset('cnn_dailymail', '3.0.0', split='test[:50]')

models = {
    "BART": "facebook/bart-large-cnn",
    "DistilBART": "sshleifer/distilbart-cnn-12-6",
}

summarizers = {name: pipeline("summarization", model=model_name) for name, model_name in models.items()}

def generate_summary(summarizer, input_text):
    """
    Generates a summary using a specified NLP model.

    :param summarizer: The summarization model pipeline.
    :param input_text: The text to be summarized.
    :return: The generated summary text.
    """

    if len(input_text.split()) > 512:
        input_text = ' '.join(input_text.split()[:512])

    summary = summarizer(input_text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def calculate_rouge_scores(reference, generated):
    """
    Calculates ROUGE scores to evaluate the quality of text summaries.

    :param reference: The reference text against which to evaluate the generated summary.
    :param generated: The generated summary text.
    :return: Dictionary of ROUGE scores.
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    scores = scorer.score(reference, generated)
    return scores

for article in dataset:
    reference = article['highlights']
    for name, summarizer in summarizers.items():
        generated_summary = generate_summary(summarizer, article['article'])
        rouge_scores = calculate_rouge_scores(reference, generated_summary)
        print(f"Model: {name}")
        print("ROUGE Scores:", rouge_scores)
        print("-" * 80)
