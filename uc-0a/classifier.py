"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "flooded", "waterlogged", "water logging", "inundat"],
    "Streetlight": ["streetlight", "street light", "lights out", "dark", "flicker", "sparking"],
    "Waste": ["garbage", "waste", "trash", "bins", "dumped", "dead animal", "smell"],
    "Noise": ["noise", "music", "loud", "midnight", "sound"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken", "tiles", "upturned", "manhole", "footpath"],
    "Heritage Damage": ["heritage", "monument", "old city", "historic"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "sunstroke", "dehydration"],
    "Drain Blockage": ["drain blocked", "drainage", "blocked drain", "clogged drain", "manhole blocked"],
}


def _safe_text(value) -> str:
    return "" if value is None else str(value).strip()


def _contains_any(text: str, words) -> list:
    hits = []
    for w in words:
        if w in text:
            hits.append(w)
    return hits

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = ""
    description = ""

    if isinstance(row, dict):
        complaint_id = _safe_text(row.get("complaint_id"))
        description = _safe_text(row.get("description"))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing so classification is uncertain.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    severity_hits = _contains_any(text, SEVERITY_KEYWORDS)

    scores = {name: 0 for name in ALLOWED_CATEGORIES if name != "Other"}
    category_hits = {name: [] for name in scores}

    for category, keys in CATEGORY_KEYWORDS.items():
        hits = _contains_any(text, keys)
        category_hits[category] = hits
        scores[category] = len(hits)

    best_category = "Other"
    flag = ""

    max_score = max(scores.values()) if scores else 0
    if max_score > 0:
        top = [c for c, s in scores.items() if s == max_score]
        best_category = top[0]
        if len(top) > 1:
            flag = "NEEDS_REVIEW"
    else:
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if severity_hits else "Standard"

    evidence = []
    if category_hits.get(best_category):
        evidence.extend(category_hits[best_category][:2])
    if severity_hits:
        evidence.extend(severity_hits[:2])

    if not evidence:
        reason = "The description is ambiguous and does not provide enough specific keywords for a confident category."
    else:
        quoted = ", ".join(f"'{w}'" for w in evidence)
        reason = f"The classification is based on keywords {quoted} in the complaint description."

    if best_category not in ALLOWED_CATEGORIES:
        best_category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Low"

    return {
        "complaint_id": complaint_id,
        "category": best_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        input_file = open(input_path, "r", newline="", encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input CSV not found: {input_path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to open input CSV '{input_path}': {exc}") from exc

    with input_file:
        reader = csv.DictReader(input_file)
        input_fields = list(reader.fieldnames or [])

        output_fields = input_fields + [
            f for f in ["category", "priority", "reason", "flag"] if f not in input_fields
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                try:
                    if not isinstance(row, dict):
                        raise ValueError("Row is not a valid dictionary record")

                    result = classify_complaint(row)
                    writer.writerow({**row, **result})
                except Exception as exc:
                    complaint_id = _safe_text(row.get("complaint_id")) if isinstance(row, dict) else ""
                    fallback_row = dict(row) if isinstance(row, dict) else {}
                    fallback_row.update(
                        {
                            "complaint_id": complaint_id,
                            "category": "Other",
                            "priority": "Low",
                            "reason": f"Malformed row encountered: {exc}.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
                    writer.writerow(fallback_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
