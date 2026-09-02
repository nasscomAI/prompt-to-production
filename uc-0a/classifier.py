"""UC-0A complaint classifier."""

import argparse
import csv
from pathlib import Path

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

ALLOWED_CATEGORIES = {
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
}


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _pick_category(description: str) -> tuple[str, bool]:
    text = _normalize(description)
    if not text:
        return "Other", True

    if "pothole" in text:
        return "Pothole", False
    if any(word in text for word in ["flood", "flooded", "waterlogged", "knee-deep", "inaccessible", "rainwater"]):
        return "Flooding", False
    if any(word in text for word in ["streetlight", "streetlights", "lights out", "light flickering", "sparking", "electrical hazard"]):
        return "Streetlight", False
    if any(word in text for word in ["garbage", "waste", "overflowing", "bulk waste", "dead animal", "smell affecting shoppers"]):
        return "Waste", False
    if any(word in text for word in ["music", "loud", "noise", "midnight", "disturbance"]):
        return "Noise", False
    if any(word in text for word in ["road surface cracked", "cracked and sinking", "tiles broken", "upturned", "footpath", "manhole cover missing"]):
        return "Road Damage", False
    if "heritage" in text and any(word in text for word in ["damage", "cracked", "broken", "lights"]):
        return "Heritage Damage", False
    if any(word in text for word in ["heat", "heat hazard", "sun", "temperature"]):
        return "Heat Hazard", False
    if any(word in text for word in ["drain blocked", "drain blockage", "blocked drain", "clogged drain", "blocked"]):
        return "Drain Blockage", False

    if any(word in text for word in ["risk", "concern", "reported"]):
        return "Other", True
    return "Other", True


def _pick_priority(description: str) -> str:
    text = _normalize(description)
    if any(word in text for word in SEVERITY_KEYWORDS):
        return "Urgent"
    if "noise" in text or "music" in text:
        return "Low"
    return "Standard"


def _build_reason(description: str, category: str) -> str:
    text = (description or "").strip()
    if not text:
        return "No descriptive text was available, so the category could not be justified from the record."

    cited = []
    lowered = _normalize(text)
    for keyword in [
        "pothole",
        "flooded",
        "streetlight",
        "garbage",
        "waste",
        "music",
        "noise",
        "cracked",
        "broken",
        "heritage",
        "heat",
        "drain",
        "blocked",
        "hazard",
        "injury",
        "fell",
        "child",
        "school",
    ]:
        if keyword in lowered and keyword not in cited:
            cited.append(keyword)

    if not cited:
        cited_text = text[:80]
        return f"The description states '{cited_text}' which supports the {category} classification."

    evidence = ", ".join(f"'{term}'" for term in cited[:3])
    return f"The description includes {evidence}, which matches the {category} category."


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row using strict allowed categories and urgency rules."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = row.get("description") or ""

    category, needs_review = _pick_category(description)
    priority = _pick_priority(description)
    reason = _build_reason(description, category)
    flag = "NEEDS_REVIEW" if needs_review else ""

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read complaint CSV and write classified results while preserving bad rows safely."""
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing a header row.")

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        rows = []
        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception:
                rows.append({
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The complaint row could not be classified safely from the input data.",
                    "flag": "NEEDS_REVIEW",
                })

    with output_file.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
