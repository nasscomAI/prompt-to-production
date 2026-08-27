"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import sys

CATEGORY_RULES = [
    ("Heritage Damage", ["heritage"]),
    ("Drain Blockage", ["drain blocked", "drain blockage"]),
    ("Pothole", ["pothole"]),
    ("Noise", ["music past midnight", "loud music"]),
    ("Heat Hazard", ["heat", "heatwave"]),
    ("Waste", ["garbage", "dead animal", "overflowing", "bulk waste"]),
    ("Streetlight", ["streetlight", "street light", "lights out"]),
    ("Flooding", ["flooded", "flooding", "floods"]),
    ("Road Damage", ["road surface", "footpath", "manhole cover", "manhole"]),
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]


def _determine_category(description: str) -> str | None:
    desc_lower = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                return category
    return None


def _determine_priority(description: str) -> str:
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _generate_reason(description: str, category: str) -> str:
    desc_lower = description.lower()
    for cat, keywords in CATEGORY_RULES:
        if cat == category:
            for kw in keywords:
                if kw in desc_lower:
                    return f"Description mentions '{kw}' indicating {category}"
    words = description.split()
    snippet = " ".join(words[:10])
    return f"Description: '{snippet}'"


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    category = _determine_category(description)
    if category is None:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": _determine_priority(description),
            "reason": _generate_reason(description, "Other"),
            "flag": "NEEDS_REVIEW",
        }

    priority = _determine_priority(description)
    reason = _generate_reason(description, category)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("complaint_id", "").strip()
            if not cid:
                print("Skipping row with missing complaint_id", file=sys.stderr)
                continue
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                print(f"Error processing complaint {cid}: {e}", file=sys.stderr)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
