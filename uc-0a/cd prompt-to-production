import pandas as pd

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(text):
    text_lower = text.lower()

    # Category detection
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "water" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower:
        category = "Noise"
    elif "road" in text_lower:
        category = "Road Damage"
    elif "drain" in text_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Priority detection
    if any(word in text_lower for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason (must include words from text)
    reason = f"Detected keywords in complaint: {text[:30]}"

    # Flag (if unsure)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    df = pd.read_csv(input_file)

    results = []

    for _, row in df.iterrows():
        text = row['complaint']
        category, priority, reason, flag = classify_complaint(text)

        results.append({
            "complaint": text,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
