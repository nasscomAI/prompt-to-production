"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)


def _text(row: dict, key: str = "description") -> str:
    value = row.get(key, "")
    return "" if value is None else str(value).strip()


def _has_any(text: str, phrases) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def _make_reason(description: str, category: str) -> str:
    if not description:
        return f"The complaint text is missing, so the issue is classified as {category}."

    if category == "Pothole":
        return f"The complaint mentions '{description}' and points to a pothole or hole in the road."
    if category == "Flooding":
        return f"The complaint mentions '{description}' and describes water covering the area."
    if category == "Drain Blockage":
        return f"The complaint mentions '{description}' and says the drain or manhole is blocked."
    if category == "Streetlight":
        return f"The complaint mentions '{description}' and refers to streetlights or lighting failure."
    if category == "Waste":
        return f"The complaint mentions '{description}' and describes garbage, dumping, or uncollected waste."
    if category == "Noise":
        return f"The complaint mentions '{description}' and describes unwanted noise or music."
    if category == "Road Damage":
        return f"The complaint mentions '{description}' and describes cracked, broken, or sinking road infrastructure."
    if category == "Heritage Damage":
        return f"The complaint mentions '{description}' and refers to damage affecting a heritage site or heritage street."
    if category == "Heat Hazard":
        return f"The complaint mentions '{description}' and describes an excessive heat hazard."
    return f"The complaint mentions '{description}' but does not clearly match a specific allowed category."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = _text(row, "complaint_id")
    description = _text(row, "description")
    text = description.lower()

    category = "Other"
    flag = ""

    if not description:
        flag = "NEEDS_REVIEW"
    elif _has_any(text, ("heritage",)) and _has_any(text, ("damage", "damaged", "broken", "cracked", "vandal", "collapse", "sink")):
        category = "Heritage Damage"
    elif _has_any(text, ("heat", "heatwave", "sunstroke", "dehydration", "extreme heat")):
        category = "Heat Hazard"
    elif _has_any(text, ("drain blocked", "blocked drain", "blocked sewer", "clogged drain", "clogged", "manhole", "water not draining", "drain blockage")):
        category = "Drain Blockage"
    elif _has_any(text, ("flooded", "flooding", "floods", "waterlogged", "knee-deep", "submerged", "standing in water")):
        category = "Flooding"
    elif _has_any(text, ("pothole", "potholes", "tyre damage", "tire damage", "sinkhole", "hole in road")):
        category = "Pothole"
    elif _has_any(text, ("streetlight", "street lights", "lights out", "light out", "flickering", "sparking", "dark at night", "lamp")):
        category = "Streetlight"
    elif _has_any(text, ("garbage", "waste", "litter", "bins", "dumped", "dumping", "dead animal", "trash")):
        category = "Waste"
    elif _has_any(text, ("noise", "music", "loud", "honking", "speaker", "disturbance")):
        category = "Noise"
    elif _has_any(text, ("cracked", "broken", "upturned", "sinking", "depression", "damaged", "uneven", "footpath", "road surface", "bridge approach")):
        category = "Road Damage"

    if category == "Other":
        flag = "NEEDS_REVIEW"

    if _has_any(text, SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category in {"Waste", "Noise"}:
        priority = "Low"
    else:
        priority = "Standard"

    reason = _make_reason(description, category)

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
    with open(input_path, "r", newline="", encoding="utf-8-sig") as source_file:
        reader = csv.DictReader(source_file)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row or {}))
        except Exception:
            complaint_id = _text(row or {}, "complaint_id")
            results.append(
                {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The complaint could not be classified reliably from the available row data.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as destination_file:
        writer = csv.DictWriter(destination_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
