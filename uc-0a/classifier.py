"""
UC-0A — Complaint Classifier
Deterministic keyword-based classifier. No LLM calls, no external services.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "knee-deep"]),
    ("Heritage Damage", ["heritage", "historic", "monument"]),
    ("Drain Blockage", ["drain block", "drain is block", "blocked drain", "drain blocked",
                        "stormwater", "drainage block"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "lights are out",
                     "light out", "light flicker", "flickering", "sparking", "unlit",
                     "darkness", "substation tripped", "wiring theft"]),
    ("Waste", ["garbage", "refuse", "trash", "dead animal", "waste", "dumped",
               "bins", "bin", "smell", "litter", "overflowing"]),
    ("Noise", ["music", "noise", "noisy", "loud", "shouting", "blast", "band",
               "amplifier", "drilling", "idling", "playing music"]),
    ("Heat Hazard", ["heat", "heatwave", "overheating", "extreme heat", "temperature",
                     "melting", "unbearable", "44°c", "52°c"]),
    ("Road Damage", ["road surface", "road cracked", "road collapsed", "sinking", "manhole",
                     "footpath", "broken", "upturned", "sinkhole", "crater", "subsided",
                     "buckled", "cracked"]),
]


def _matches(text: str, keywords) -> bool:
    for kw in keywords:
        if kw in text:
            return True
    return False


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description")
    description = (description or "").strip()

    # Null/empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Determine category via keyword rules (first match wins by specificity order)
    category = "Other"
    for name, keywords in CATEGORY_RULES:
        if _matches(text, keywords):
            category = name
            break

    # Determine priority
    if _matches(text, URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Determine flag
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # Build reason citing specific words from description
    reason = _build_reason(description, category, priority)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(description: str, category: str, priority: str) -> str:
    text = description.lower()

    if category == "Other":
        return f"No keyword matched '{description.strip()}'."

    # Find the matching keyword to cite
    cited = None
    for name, keywords in CATEGORY_RULES:
        if name == category:
            for kw in keywords:
                if kw in text:
                    cited = kw
                    break
            break

    reason = f"Matched '{cited}' which indicates {category.lower()}."
    if priority == "Urgent":
        for kw in URGENT_KEYWORDS:
            if kw in text:
                reason += f" Severity keyword '{kw}' present."
                break
    return reason


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norm = {k.strip(): v for k, v in row.items()}
            results.append(classify_complaint(norm))

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
    print(f"Done. Results written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
