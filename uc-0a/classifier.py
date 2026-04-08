import pandas as pd
import argparse

def classify_complaint(text):
    text = text.lower()

    category = "Other"
    priority = "Low"
    reason = ""
    flag = ""

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water" in text:
        category = "Flooding"
    elif "light" in text:
        category = "Streetlight"
    elif "waste" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"

    urgent_words = ["injury", "school", "hospital", "fire"]

    if any(word in text for word in urgent_words):
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = f"Detected category {category}"

    return category, priority, reason, flag


parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output")
args = parser.parse_args()

df = pd.read_csv(args.input)

categories = []
priorities = []
reasons = []
flags = []

for complaint in df["description"]:
    c, p, r, f = classify_complaint(str(complaint))
    categories.append(c)
    priorities.append(p)
    reasons.append(r)
    flags.append(f)

df["category"] = categories
df["priority"] = priorities
df["reason"] = reasons
df["flag"] = flags

df.to_csv(args.output, index=False)

print("Done")
