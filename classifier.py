
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# 1. Load Data
df = pd.read_csv("complaints.csv")

# 2. Train Model
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['Complaint'])
y = df['Category']
clf = LogisticRegression()
clf.fit(X, y)

def classify_with_priority(text):
    # Rule-based check for High Priority
    high_priority_keywords = ["danger", "injury", "emergency", "broken", "pothole"]
    
    if any(word in text.lower() for word in high_priority_keywords):
        category = clf.predict(vectorizer.transform([text]))[0]
        return f"{category} (HIGH PRIORITY)"
    
    # --- ADD THIS LINE BELOW ---
    # This handles normal complaints that aren't dangerous
    return clf.predict(vectorizer.transform([text]))[0]

# 3. Execution
if __name__ == "__main__":
    print("AI Code Sarathi - Complaint Classifier Loaded.")
    while True:
        text = input("\nEnter complaint (or 'exit'): ")
        if text.lower() == "exit": 
            break
        print("Result:", classify_with_priority(text))
        