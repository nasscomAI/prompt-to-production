"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import pandas as pd
import argparse

# Allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

# Severity keywords → Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


# -----------------------------
# Skill 1: classify_complaint
# -----------------------------
def classify_complaint(description):
    if not isinstance(description, str) or description.strip() == "":
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing or empty",
            "flag": "NEEDS_REVIEW"
        }

    desc = description.lower()

    # Category mapping (simple keyword rules)
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "waterlogging" in desc:
        category = "Flooding"
    elif "streetlight" in desc or "light not working" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc:
        category = "Waste"
    elif "noise" in desc or "loud" in desc:
        category = "Noise"
    elif "road damage" in desc or "road broken" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc or "blockage" in desc:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Priority logic
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"
            break

    # Reason (must cite words)
    reason = f"Identified keywords in description: '{description[:50]}'"

    # Flag ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


# -----------------------------
# Skill 2: batch_classify
# -----------------------------
def batch_classify(input_path, output_path):
    df = pd.read_csv(input_path)

    if "description" not in df.columns:
        raise Exception("[FAIL] Input CSV must contain 'description' column")

    results = []

    for _, row in df.iterrows():
        result = classify_complaint(row["description"])

        results.append({
            "description": row["description"],
            "category": result["category"],
            "priority": result["priority"],
            "reason": result["reason"],
            "flag": result["flag"]
        })

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_path, index=False)

    print(f"[SUCCESS] Results saved to {output_path}")


# -----------------------------
# MAIN
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()