from transformers import pipeline

input_file_path = '../transcriptions/test2.txt'

output_file_path = '../backend/output_summary.txt'

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

prompt = "Create a concise and engaging summary that captures the essential features and visual elements of the topic. Describe its main attributes , in a way that can be visually interpreted for image creation. This summary should be adaptable for YouTube video covers."

def load_text(file_path, prompt):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        full_text = prompt + " " + text
        return full_text[:1024]

def generate_summary(text):
    result = summarizer(text, max_length=120, min_length=50, do_sample=False)
    return result[0]['summary_text']

text_with_prompt = load_text(input_file_path, prompt)

summary = generate_summary(text_with_prompt)

with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(summary)

print("Podsumowanie zostało zapisane w:", output_file_path)

