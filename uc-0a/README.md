import pandas as pd
import argparse

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(description):
    text = str(description).lower()

    # Category detection
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water" in text:
        category = "Flooding"
    elif "streetlight" in text or "light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text or "trash" in text:
        category = "Waste"
    elif "noise" in text or "loud" in text:
        category = "Noise"
    elif "road damage" in text or "broken road" in text:
        category = "Road Damage"
    elif "heritage" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text or "block" in text:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Priority detection
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    # Reason (must reference description)
    reason = f"Classification based on keywords found in description: '{description}'"

    # Flag for ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    df = pd.read_csv(input_file)

    categories = []
    priorities = []
    reasons = []
    flags = []

    for desc in df["description"]:
        category, priority, reason, flag = classify_complaint(desc)

        categories.append(category)
        priorities.append(priority)
        reasons.append(reason)
        flags.append(flag)

    df["category"] = categories
    df["priority"] = priorities
    df["reason"] = reasons
    df["flag"] = flags

    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)