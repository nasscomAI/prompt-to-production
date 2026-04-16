from transformers import pipeline

summarizer = pipline("summarization", model="facebook/bart-large-cnn")

text = """Your HR policy text goes here..."""

summary = summarizer(text, max_length=100, min_length=30,do_sample=False )

print("Summary:", summary[0]['summary_text'])