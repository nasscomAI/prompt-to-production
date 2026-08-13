"""
UC-0A — Complaint Classifier
Enforces the exact schema and rules from agents.md and skills.md:
category is one of the ten allowed strings, priority is Urgent/Standard/Low,
reason is one sentence citing words from the description, flag is blank or
NEEDS_REVIEW.
"""
import argparse
import csv

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

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse", "fall",
]

WASTE_SOLID = [
    "garbage", "waste", "trash", "litter", "bins", "bin",
    "dead animal", "rubbish", "dumped",
]
WASTE_ODOR = ["smell", "stink"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogged", "submerged", "standing water", "standing in water"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "flickering", "sparking", "lamp", "dark at night", "after dark", "dark", "unlit"],
    "Waste": WASTE_SOLID + WASTE_ODOR,
    "Noise": ["music", "noise", "loud", "honking", "midnight", "band", "amplifier"],
    "Road Damage": ["road surface", "cracked", "sinking", "subsided", "subsidence", "buckled", "buckling", "manhole", "footpath", "pavement", "paving", "tiles", "broken and", "broken up", "broken tiles", "glass"],
    "Heritage Damage": ["heritage", "monument", "historic", "defaced"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "temperature", "°c", "melting", "bubbling", "burns"],
    "Drain Blockage": ["drain", "blocked", "clogged", "sewage", "blockage"],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _waste_hits(text: str):
    solid = [kw for kw in WASTE_SOLID if kw in text]
    if solid:
        return solid + [kw for kw in WASTE_ODOR if kw in text]
    return []


def _score_categories(text: str):
    scores = {}
    matched = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "Waste":
            hits = _waste_hits(text)
        else:
            hits = [kw for kw in keywords if kw in text]
        scores[category] = len(hits)
        matched[category] = hits
    return scores, matched


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in text]
    priority = "Urgent" if urgent_hits else "Standard"
    urgent_note = f"; urgent because it contains {urgent_hits[0]!r}" if urgent_hits else ""

    scores, matched = _score_categories(text)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top, top_score = ranked[0]
    second, second_score = ranked[1]

    if top_score == 0:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"Ambiguous: no category matches the description{urgent_note}.",
            "flag": "NEEDS_REVIEW",
        }

    if top_score == second_score:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"Ambiguous: matches both {top!r} and {second!r}{urgent_note}.",
            "flag": "NEEDS_REVIEW",
        }

    hits = matched[top]
    if top == "Noise" and priority == "Standard":
        priority = "Low"

    quoted = ", ".join(f"'{kw}'" for kw in hits)
    reason = f"{top} because the description mentions {quoted}{urgent_note}."

    return {
        "complaint_id": complaint_id,
        "category": top,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=2):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append({
                    "complaint_id": row.get("complaint_id", str(row_number)),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
