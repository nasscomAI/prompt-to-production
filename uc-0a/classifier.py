"""
UC-0A — Complaint Classifier
Build guided by uc-0a/agents.md and uc-0a/skills.md.

Run:
  python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _match_category(description: str) -> str:
    """Heuristic mapping of description text to one allowed category.

    Returns "Other" when no confident signal is present.
    """
    text = description.lower()

    # Heritage
    if "heritage" in text:
        return "Heritage Damage"

    # Heat
    if "heat" in text:
        return "Heat Hazard"

    # Noise
    if any(w in text for w in ["music", "noise", "loud", "midnight"]):
        return "Noise"

    # Streetlight
    if any(w in text for w in ["streetlight", "street light", "light", "lights out", "dark", "spark"]) \
            and "heritage" not in text:
        return "Streetlight"

    # Waste / garbage
    if any(w in text for w in ["garbage", "waste", "bin", "dumped", "dead animal", "smell", "overflow"]):
        return "Waste"

    # Flooding vs Drain Blockage
    if any(w in text for w in ["flood", "flooded", "knee-deep", "inaccessible", "stranded"]):
        if any(w in text for w in ["drain", "manhole", "blocked", "blockage"]):
            return "Drain Blockage"
        return "Flooding"

    # Pothole
    if any(w in text for w in ["pothole", "potholes", "tyre", "tire", "vehicle"]):
        return "Pothole"

    # Road Damage (general road surface problems)
    if any(w in text for w in ["road", "footpath", "tiles", "cracked", "sinking", "surface", "upturned", "missing cover", "manhole cover"]):
        if "cover" in text or "manhole" in text or "footpath" in text:
            return "Road Damage"
        return "Road Damage"

    return "Other"


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided; category undeterminable.",
            "flag": "NEEDS_REVIEW",
        }

    category = _match_category(description)

    lowered = description.lower()
    has_severity = any(kw in lowered for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = _build_reason(description, category, has_severity)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(description: str, category: str, has_severity: bool) -> str:
    snippet = description
    if len(snippet) > 90:
        snippet = snippet[:87] + "..."
    sev_note = " Severity keyword present." if has_severity else ""
    return f"Classified as {category} based on: \"{snippet}\".{sev_note}"


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    reviewed = 0
    written = 0
    with open(input_path, newline="", encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never crash on a bad row
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            if result["flag"] == "NEEDS_REVIEW":
                reviewed += 1
            writer.writerow(result)
            written += 1
    print(f"Classified {written} rows. {reviewed} flagged NEEDS_REVIEW.")
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
