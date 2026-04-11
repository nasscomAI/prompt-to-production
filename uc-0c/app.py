text = """
Artificial Intelligence is transforming industries by automating tasks,
improving decision making and enabling new innovations.
Organizations are increasingly using AI to analyze large volumes of data
and generate insights that help them stay competitive.
"""

sentences = text.split(".")
summary = sentences[0] + "."

print("Original Text:\n", text)
print("\nSummary:\n", summary)