import argparse
import pandas as pd

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(text):
    text_lower = str(text).lower()

    # ---------- Category detection ----------
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "waterlogging" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower or "loud" in text_lower:
        category = "Noise"
    elif "road" in text_lower:
        category = "Road Damage"
    elif "heritage" in text_lower:
        category = "Heritage Damage"
    elif "heat" in text_lower:
        category = "Heat Hazard"
    elif "drain" in text_lower or "sewage" in text_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    # ---------- Priority detection ----------
    if any(word in text_lower for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # ---------- Reason ----------
    reason = f"Detected keywords in description: '{text[:50]}'"

    # ---------- Flag ----------
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    df = pd.read_csv(input_file)

    results = []

    for _, row in df.iterrows():
        text = row.get("description", "")

        category, priority, reason, flag = classify_complaint(text)

        results.append({
            "description": text,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False)

    print(f"✅ Output saved to {output_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()