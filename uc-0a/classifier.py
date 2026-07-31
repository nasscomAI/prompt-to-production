"""
UC-0A — Complaint Classifier
Implementation for Nasscom AI Code Sarathi workshop.
"""
import argparse
import csv
from typing import Dict

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    location = row.get("location", "").strip()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No complaint description provided.",
            "flag": "NEEDS_REVIEW",
        }

    text_lower = (desc + " " + location).lower()

    # Priority determination based on severity keywords
    is_urgent = any(kw in text_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    category = "Other"
    flag = ""

    # Category classification based on taxonomy rules
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or ("water" in text_lower and "standing" in text_lower):
        category = "Flooding"
        if "drain" in text_lower:
            flag = "NEEDS_REVIEW"
    elif "heritage" in text_lower and ("light" in text_lower or "dark" in text_lower):
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
    elif "streetlight" in text_lower or "lights out" in text_lower or "lamp" in text_lower:
        category = "Streetlight"
    elif any(w in text_lower for w in ["garbage", "waste", "trash", "dead animal", "dumped"]):
        category = "Waste"
    elif any(w in text_lower for w in ["music", "noise", "loudspeaker", "sound"]):
        category = "Noise"
    elif "heritage" in text_lower:
        category = "Heritage Damage"
    elif any(w in text_lower for w in ["heat", "heatwave"]):
        category = "Heat Hazard"
    elif any(w in text_lower for w in ["drain", "manhole", "gutter"]):
        category = "Drain Blockage"
    elif any(w in text_lower for w in ["cracked", "sinking", "footpath", "road surface", "tile"]):
        category = "Road Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # One sentence reason citing specific words from description
    clean_desc = desc.replace("\n", " ").strip()
    if not clean_desc.endswith("."):
        clean_desc += "."
    reason = f"Complaint cites: {clean_desc}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
