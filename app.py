from transformers import pipeline

summarizer = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"
)

text = """
Artificial Intelligence is transforming industries by automating tasks,
improving decision making and enabling new innovations.
"""

result = summarizer(f"summarize: {text}", max_length=80)

print(result[0]['generated_text'])