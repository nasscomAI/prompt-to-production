import pandas as pd

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORIES = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "light": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage"
}


def classify_complaint(text):
    text_lower = text.lower()

    # Category
    category = "Other"
    for key in CATEGORIES:
        if key in text_lower:
            category = CATEGORIES[key]
            break

    # Priority
    priority = "Low"
    for word in SEVERITY_KEYWORDS:
        if word in text_lower:
            priority = "Urgent"
            break
    else:
        priority = "Standard"

    # Reason
    reason = f"Detected keywords in complaint: {text[:50]}"

    # Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    df = pd.read_csv(input_file)

    results = []

    for _, row in df.iterrows():
        category, priority, reason, flag = classify_complaint(row["description"])

        results.append({
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        })

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)