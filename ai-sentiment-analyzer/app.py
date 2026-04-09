text = input("Enter a sentence: ")

positive_words = ["good", "happy", "excellent", "great"]
negative_words = ["bad", "sad", "terrible", "worst"]

if any(word in text.lower() for word in positive_words):
    sentiment = "Positive"
elif any(word in text.lower() for word in negative_words):
    sentiment = "Negative"
else:
    sentiment = "Neutral"

print("Sentiment:", sentiment)