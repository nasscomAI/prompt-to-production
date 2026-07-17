"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re


URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole"],
    "Flooding":        ["flooded", "flooding", "flood", "submerged", "waterlogging"],
    "Streetlight":     ["streetlight", "lights out", "lamp post", "unlit"],
    "Waste":           ["garbage", "overflowing bins", "dead animal", "trash", "litter", "dump", "waste"],
    "Noise":           ["noise", "music", "loud", "honking", "party", "band playing"],
    "Road Damage":     ["road surface", "cracked", "sinking", "footpath", "pavement", "road damage", "paving", "road collapsed", "subsided"],
    "Heritage Damage": ["heritage", "historic"],
    "Heat Hazard":     ["heatwave", "heat hazard", "extreme heat", "heat", "temperature", "melting", "\u00b0c"],
    "Drain Blockage":  ["manhole", "drain blocked", "blocked drain", "drainage", "sewer"],
}


def _classify(desc: str):
    if not desc or not desc.strip():
        return "Other", "NEEDS_REVIEW", []

    desc_lower = desc.lower()

    best_cat = "Other"
    best_score = 0
    best_keywords = []
    tie = False

    for cat, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in desc_lower]
        score = len(matched)
        if score > best_score:
            best_cat = cat
            best_score = score
            best_keywords = matched
            tie = False
        elif score == best_score and score > 0:
            tie = True

    if best_score == 0 or tie:
        return "Other", "NEEDS_REVIEW", []

    return best_cat, "", best_keywords


def _get_priority(desc: str) -> str:
    if not desc:
        return "Standard"
    desc_lower = desc.lower()
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _get_reason(desc: str, category: str, matched: list) -> str:
    if not desc or not desc.strip():
        return "Empty description"

    desc_lower = desc.lower()
    citations = list(matched)

    if len(citations) < 2:
        words = re.findall(r"[A-Za-z]+", desc_lower)
        for w in words:
            if len(w) > 2 and w not in citations:
                citations.append(w)
                if len(citations) >= 2:
                    break

    if len(citations) >= 2:
        return f"Description mentions '{citations[0]}' and '{citations[1]}', indicating {category}."
    elif len(citations) == 1:
        return f"Description mentions '{citations[0]}', indicating {category}."
    return f"Classified as {category} based on description."


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    category, flag, matched_keywords = _classify(description)
    priority = _get_priority(description)
    reason = _get_reason(description, category, matched_keywords)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader):
                try:
                    result = classify_complaint(row)
                except Exception:
                    result = {
                        "complaint_id": row.get("complaint_id", f"row_{i}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Error processing row",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
