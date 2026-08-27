import textwrap

text = """
Artificial Intelligence is transforming industries by automating tasks,
improving decision making and enabling innovation. Many companies are
using AI to analyze large amounts of data and generate insights.
"""

summary = textwrap.shorten(text, width=100)

print("Original Text:\n")
print(text)

print("\nSummary:\n")
print(summary)