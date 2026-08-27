"""
UC-0A — Complaint Classifier
Classifies citizen complaints per agents.md / skills.md enforcement rules.
"""
import argparse
import csv

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "light out", "flickering", "sparking", "unlit", "darkness", "substation", "power cut"]),
    ("Noise", ["music", "noise", "loud", "honking", "speakers", "amplifiers", "wedding band", "drilling", "idling"]),
    ("Waste", ["garbage", "waste", "dead animal", "dumped", "trash", "bins", "carcass", "litter", "overflowing"]),
    ("Flooding", ["flood", "waterlogged", "submerged", "standing water", "knee-deep", "underwater", "rainwater"]),
    ("Road Damage", ["road surface", "road collapsed", "cracked", "sinking", "subsided", "subsidence", "manhole", "pavement", "footpath", "tiles", "buckled", "upturned", "crater"]),
    ("Drain Blockage", ["drain", "drainage", "sewage", "gutter", "clogged", "blocked"]),
    ("Heritage Damage", ["heritage", "historic", "monument", "cobblestone", "historical"]),
    ("Heat Hazard", ["heat", "heatwave", "temperature", "scorching", "melting", "bubbling", "tarmac", "full sun", "degree"]),
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse", "gas leak"]
RISK_PHRASES = [
    "safety concern", "health concern", "risk", "stranded", "inaccessible",
    "standing in water", "tyre damage", "tyre blowouts", "vehicles", "passengers",
    "commuters", "public road", "pedestrians", "unsafe", "dangerous", "structural",
    "subsided", "subsidence", "burns", "dengue",
]
LOW_MARKERS = [
    "music", "noise", "wedding band", "amplifiers", "drilling", "idling",
    "smell", "odor", "dark at night", "lights out", "flickering", "unlit", "darkness",
]

FLOOD_RISK_PHRASES = ["flooding risk", "flood risk", "at flooding risk"]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _quote_context(description: str, keyword) -> str:
    if not keyword:
        return description[:100].strip()
    idx = description.lower().find(keyword)
    if idx == -1:
        return description[:100].strip()
    end = min(len(description), idx + len(keyword) + 40)
    snippet = description[idx:end].strip().strip(".,")
    return snippet


def _match_category(description: str):
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if category == "Flooding" and any(p in text for p in FLOOD_RISK_PHRASES):
            continue
        for kw in keywords:
            if kw in text:
                return category, kw
    return "Other", None


def _match_priority(description: str) -> str:
    text = description.lower()
    if any(kw in text for kw in URGENT_KEYWORDS):
        return "Urgent"
    if any(p in text for p in RISK_PHRASES):
        return "Standard"
    if any(m in text for m in LOW_MARKERS):
        return "Low"
    return "Standard"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "") or "").strip()
    description = str(row.get("description", "") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_keyword = _match_category(description)
    priority = _match_priority(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    quote = _quote_context(description, matched_keyword)

    if flag:
        reason = f'Description quotes "{quote}" but the category is ambiguous; flagged NEEDS_REVIEW for manual review.'
    else:
        reason = f'Description cites "{quote}", indicating {category} with {priority} priority.'

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
    Flags unclassifiable rows, never crashes on bad rows, produces output for all rows.
    """
    rows = []
    with open(input_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            try:
                rows.append(classify_complaint(row))
            except Exception:
                cid = str(row.get("complaint_id", f"row-{line_no}") or f"row-{line_no}").strip()
                rows.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be parsed; flagged for manual review.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
