#classifier.py
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.native_bayes import MultinomialNB

complanits = [
    "Internet not working",
    "Bill is too high",
    "Poor customer service"
]

labels = ["Technical", "Billing", "Service"]

vectorizer = CountVectorizer()
x = vectorizer.fit_transform(complaints)

model = MultinomialNB()
model.fit(X, labels)

test = ["Slow connection"]
print("Prediction:", model.predict(vectorizer.transform(test))[0])
