import pandas as pd
import re

# -------------------------------
# Configuration
# -------------------------------

INPUT_FILE = r"C:\Users\User\OneDrive\Documents\GitHub\AbhiramAgarwal-NewDelhi\data\city-test-files\test_pune.csv"
OUTPUT_FILE = r"C:\Users\User\OneDrive\Documents\GitHub\AbhiramAgarwal-NewDelhi\uc-0a\results_pune.csv"

# Severity keywords (Urgent)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell",
    "collapse"
]

# Category keywords
CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole", "crater", "road hole", "big hole"
    ],

    "Flooding": [
        "flood", "waterlogging", "water logged",
        "overflow", "standing water", "heavy rain"
    ],

    "Streetlight": [
        "streetlight", "street light", "lamp",
        "light not working", "dark road",
        "no light", "electric pole"
    ],

    "Waste": [
        "garbage", "waste", "trash", "litter",
        "dump", "rubbish", "dustbin"
    ],

    "Noise": [
        "noise", "loud", "speaker", "dj",
        "music", "horn", "construction noise"
    ],

    "Road Damage": [
        "road damage", "broken road",
        "cracked road", "damaged road",
        "uneven road"
    ],

    "Heritage Damage": [
        "heritage", "historic",
        "monument", "statue"
    ],

    "Heat Hazard": [
        "heat", "heatwave", "extreme heat",
        "hot weather", "sun exposure"
    ],

    "Drain Blockage": [
        "drain", "blocked drain",
        "drain blockage", "sewer",
        "clogged drain", "gutter"
    ]
}


# -------------------------------
# Complaint Classifier
# -------------------------------

def classify_complaint(description):

    text = str(description).lower()

    matched_categories = []

    # Find matching categories
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                matched_categories.append(category)
                break

    # Determine category
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""

    elif len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"

    else:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"

    # Determine priority
    severity_found = []

    for word in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            severity_found.append(word)

    if severity_found:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Generate reason
    if severity_found:
        reason = (
            f"Classified as {category} because description contains "
            f"severity keyword(s): {', '.join(severity_found)}."
        )

    elif category != "Other":
        keyword_used = ""

        for k in CATEGORY_KEYWORDS[category]:
            if k in text:
                keyword_used = k
                break

        reason = (
            f"Classified as {category} because the description mentions "
            f"'{keyword_used}'."
        )

    else:
        reason = (
            "Complaint does not clearly match any allowed category."
        )

    return category, priority, reason, flag


# -------------------------------
# Batch Classification
# -------------------------------

def batch_classify(input_file, output_file):

    df = pd.read_csv(input_file)

    categories = []
    priorities = []
    reasons = []
    flags = []

    for complaint in df["description"]:

        category, priority, reason, flag = classify_complaint(complaint)

        categories.append(category)
        priorities.append(priority)
        reasons.append(reason)
        flags.append(flag)

    df["category"] = categories
    df["priority"] = priorities
    df["reason"] = reasons
    df["flag"] = flags

    df.to_csv(output_file, index=False)

    print("----------------------------------")
    print("Classification Completed")
    print("----------------------------------")
    print("Input :", input_file)
    print("Output:", output_file)
    print(f"Rows processed: {len(df)}")


# -------------------------------
# Main Program
# -------------------------------

if __name__ == "__main__":

    batch_classify(INPUT_FILE, OUTPUT_FILE)