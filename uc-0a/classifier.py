"""
UC-0A — Complaint Classifier
Starter file. Build this using your AI tool guided by the UC-0A agents and skills definitions.
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

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "blocked drain", "manhole cover missing", "manhole missing"]),
    ("Streetlight", ["streetlight", "lights out", "light out", "flickering", "sparking", "dark at night", "dark at night"]),
    ("Noise", ["music", "noise", "speaker", "party", "loud", "midnight"]),
    ("Waste", ["garbage", "waste", "smell", "dumped", "overflowing bins", "dead animal", "health concern"]),
    ("Heat Hazard", ["heat", "heatwave", "sunstroke", "hot weather", "heat hazard"]),
    ("Heritage Damage", ["heritage", "historic", "heritage zone", "heritage street"]),
    ("Flooding", ["flooded", "floods", "standing in water", "rain", "knee-deep", "inaccessible", "water"]),
    ("Road Damage", ["cracked", "sinking", "depression", "depressed", "tiles broken", "upturned", "road surface cracked", "bridge approach floods", "bus stand flooded"]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _normalize_text(value: str) -> str:
    if value is None:
        return ""
    return value.strip().lower()


def _matches_any(text: str, patterns):
    return [pattern for pattern in patterns if pattern in text]


def _select_category(description: str) -> tuple[str, str]:
    text = _normalize_text(description)
    if not text:
        return "Other", "No description provided."

    scores = {}
    matches = {}
    for category, patterns in CATEGORY_RULES:
        hits = _matches_any(text, patterns)
        if hits:
            scores[category] = len(hits)
            matches[category] = hits

    if not scores:
        return "Other", "No category keywords matched."

    sorted_categories = sorted(
        scores.items(),
        key=lambda item: (-item[1], [rule[0] for rule in CATEGORY_RULES].index(item[0])),
    )
    chosen_category = sorted_categories[0][0]
    chosen_match = matches[chosen_category][0]

    # Protect against heritage streetlight ambiguity: prefer Streetlight when streetlight keywords are present.
    if chosen_category == "Heritage Damage" and "streetlight" in text:
        chosen_category = "Streetlight"
        chosen_match = "streetlight"

    return chosen_category, chosen_match


def _needs_review(description: str, category: str, matched_phrase: str) -> str:
    text = _normalize_text(description)
    if not text:
        return "NEEDS_REVIEW"
    if category == "Other":
        return "NEEDS_REVIEW"
    if category == "Heritage Damage" and "streetlight" in text and "heritage" in text:
        return "NEEDS_REVIEW"
    return ""


def _classify_priority(description: str) -> str:
    text = _normalize_text(description)
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, matched_phrase: str) -> str:
    text = description.strip()
    if not text:
        return "Unable to classify due to missing description."

    phrase = matched_phrase or category
    reason = f"Classified as {category} because description mentions '{phrase}'."
    if category == "Other":
        return f"Unable to map the complaint to a specific category; description contains '{phrase}'."
    return reason


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    description = _normalize_text(row.get("description") if isinstance(row, dict) else "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Unable to classify due to missing description.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_phrase = _select_category(description)
    priority = _classify_priority(description)
    reason = _build_reason(row.get("description", ""), category, matched_phrase)
    flag = _needs_review(description, category, matched_phrase)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category exceeded allowed values and was set to Other."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row_index, row in enumerate(reader, start=1):
                if not row:
                    continue
                try:
                    classified = classify_complaint(row)
                except Exception:
                    classified = {
                        "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Unable to classify due to internal error.",
                        "flag": "NEEDS_REVIEW",
                    }
                rows.append(classified)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {input_path}") from exc

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
