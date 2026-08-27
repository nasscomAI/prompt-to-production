"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "pot hole", "crater", "tyre damage", "tire damage"]),
    ("Flooding", ["flood", "flooded", "flooding", "waterlogging", "water logged", "water log", "knee-deep", "standing water", "inundated"]),
    ("Streetlight", ["streetlight", "street light", "streetlights", "street lights", "lights out", "light out", "flickering", "dark at night", "darkness"]),
    ("Waste", ["garbage", "bin", "waste", "dump", "dumped", "trash", "overflowing", "smell", "litter", "dead animal", "animal not removed"]),
    ("Noise", ["noise", "loud", "music", "party", "honking", "sound pollution", "past midnight", "weeknights", "late night"]),
    ("Road Damage", ["cracked", "sinking", "road surface", "broken tiles", "footpath tiles", "manhole cover missing", "upturned", "pavement", "footpath"]),
    ("Heritage Damage", ["heritage", "historic", "monument", "heritage street", "heritage building"]),
    ("Heat Hazard", ["heat", "hot", "heatwave", "scorching", "temperature"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "blocked drain", "clogged drain", "gutter", "sewage", "drainage blocked"]),
]
SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]
LOW_PRIORITY_KEYWORDS = [
    "smell",
    "music",
    "noise",
    "late night",
    "past midnight",
    "weeknights",
    "overflowing garbage",
]


def _find_matches(description: str, phrases: list[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase in description]


def _choose_category(description: str) -> tuple[str, list[str], str]:
    matches_by_category = {}
    for category, phrases in CATEGORY_KEYWORDS:
        matched = _find_matches(description, phrases)
        if matched:
            matches_by_category[category] = matched

    if not matches_by_category:
        return "Other", [], ""

    # Prefer the first matching category in the configured list, but note ambiguity.
    chosen_category = next(iter(matches_by_category))
    chosen_phrases = matches_by_category[chosen_category]
    if len(matches_by_category) > 1:
        # If more than one strong category appears, choose the one that shows first
        # in our explicit schema order and mark this as ambiguous.
        for category, _ in CATEGORY_KEYWORDS:
            if category in matches_by_category:
                chosen_category = category
                chosen_phrases = matches_by_category[category]
                break
    return chosen_category, chosen_phrases, "NEEDS_REVIEW" if len(matches_by_category) > 1 else ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description; cannot classify with confidence.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()
    category, matched_phrases, ambiguity_flag = _choose_category(description_lower)

    severity_matches = _find_matches(description_lower, SEVERITY_KEYWORDS)
    if severity_matches:
        priority = "Urgent"
    elif category in {"Noise", "Waste"} or _find_matches(description_lower, LOW_PRIORITY_KEYWORDS):
        priority = "Low"
    else:
        priority = "Standard"

    if matched_phrases:
        top_phrase = matched_phrases[0]
        if priority == "Urgent" and severity_matches:
            reason = (
                f"Description mentions '{top_phrase}' and severity keyword '{severity_matches[0]}', so category is {category} and priority is Urgent."
            )
        else:
            reason = f"Description mentions '{top_phrase}', so category is {category} and priority is {priority}."
    elif severity_matches:
        reason = (
            f"Description mentions severity keyword '{severity_matches[0]}', so priority is Urgent; category defaults to Other."
        )
    else:
        reason = f"Complaint text could not be matched to a strong category; category set to {category}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": ambiguity_flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as exc:
                    complaint_id = (row.get("complaint_id") or "").strip()
                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed: {exc}",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
