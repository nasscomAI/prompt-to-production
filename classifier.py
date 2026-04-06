import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load the CSV
df = pd.read_csv("complaints.csv")

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    df['Complaint'], df['Category'], test_size=0.2, random_state=42
)

# Convert text to numerical features
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train a classifier
clf = LogisticRegression()
clf.fit(X_train_vec, y_train)

# Test the classifier
y_pred = clf.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Predict new complaints
while True:
    text = input("\nEnter a complaint (or 'exit' to quit): ")
    if text.lower() == "exit":
        break
    pred = clf.predict(vectorizer.transform([text]))
    print("Predicted Category:", pred[0])