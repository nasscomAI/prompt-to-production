"""
UC-0A — Complaint Classifier
RICE-enforced classification. Rules sourced from agents.md, structure from skills.md.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogged"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "lamp"],
    "Waste": ["garbage", "waste", "dead animal", "dumped", "dumping", "bins", "smell"],
    "Noise": ["noise", "music", "loudspeaker", "past midnight"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles broken", "manhole cover"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke"],
    "Drain Blockage": ["drain", "drainage", "sewage", "blocked"],
}


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    text = description.lower()
    complaint_id = row.get("complaint_id") or ""

    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                matched.append((category, keyword))
                break

    unique_categories = list(dict.fromkeys(c for c, _ in matched))
    ambiguous = len(unique_categories) != 1

    if len(unique_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif ambiguous:
        category = unique_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = unique_categories[0]
        flag = ""

    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    priority = "Urgent" if severity_hits else "Standard"

    evidence = matched[0][1] if matched else "no category keyword matched"
    reason = (
        f"Category \"{category}\" based on description containing \"{evidence}\""
        f" (citing: \"{evidence}\" from the description); "
        f"priority {priority} because description "
        f"{'contains ' + repr(severity_hits[0]) if severity_hits else 'has no severity keywords'}."
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows_out = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows_out.append(classify_complaint(row))
            except Exception as e:
                rows_out.append({
                    "complaint_id": row.get("complaint_id") or "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["complaint_id", "category", "priority", "reason", "flag"],
        )
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
