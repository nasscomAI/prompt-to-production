from transformers import pipeline

summarizer = pipeline("text2text-generation", model="t5-small")

text = "summarize: Artificial Intelligence is transforming industries by automating tasks and improving decision making."

output = summarizer(text, max_length=50)

print("Summary:\n", output[0]['generated_text'])
