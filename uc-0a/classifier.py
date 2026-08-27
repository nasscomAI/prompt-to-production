"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "tyre damage"]),
    ("Flooding", ["flooded", "flooding", "floods", "knee-deep", "waterlog", "submerged", "inundat"]),
    ("Streetlight", ["streetlight", "lights out", "light out", "dark at night", "flickering", "lighting"]),
    ("Waste", ["garbage", "overflowing bin", "dead animal", "dumping", "bulk waste", "trash", "waste"]),
    ("Noise", ["noise", "music", "loud", "wedding", "party", "honking"]),
    ("Road Damage", ["road surface", "cracked and sinking", "cracked", "sinking", "footpath", "tiles broken"]),
    ("Heritage Damage", ["heritage street", "heritage"]),
    ("Heat Hazard", ["heat", "heatwave", "temperature", "sunstroke"]),
    ("Drain Blockage", ["drain", "drainage", "blocked drain", "manhole", "sewer"]),
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def classify_complaint(row: dict) -> dict:
    desc = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = desc.lower()
    matched = []

    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc_lower:
                matched.append(category)
                break

    if not matched:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": f"Description does not clearly map to any specific category: '{desc[:120]}'.",
            "flag": "NEEDS_REVIEW",
        }

    category = matched[0]
    flag = "NEEDS_REVIEW" if len(matched) > 1 else ""

    cited = []
    for c, kws in CATEGORY_KEYWORDS:
        for kw in kws:
            if kw in desc_lower and kw not in cited:
                cited.append(kw)

    reason = f"Description mentions '{', '.join(cited[:3])}' — classified as {category}."
    severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    if severity_found:
        priority = "Urgent"
        reason += f" Severity keywords present: {', '.join(severity_found)}."
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Classification error.",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
