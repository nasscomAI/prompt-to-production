import argparse
import csv
import re


CATEGORIES = {
    "Pothole": ("pothole", "potholes"),
    "Flooding": ("flood", "floods", "flooded", "flooding", "rainwater", "waterlogging", "waterlogged"),
    "Streetlight": ("streetlight", "streetlights", "street light", "lamp post", "street lamp", "unlit", "darkness", "substation tripped"),
    "Waste": ("garbage", "waste", "trash", "litter", "dumping", "dustbin", "dead animal"),
    "Noise": ("noise", "noisy", "loud", "music", "band", "amplifier", "drilling", "idling", "honking", "honk", "loud music"),
    "Road Damage": ("road damage", "damaged road", "road collapsed", "road surface", "road subsided", "surface buckled", "cobblestones", "paving removed", "upturned paving", "footpath broken", "crater", "crack", "cracked", "broken road", "footpath tiles", "manhole", "asphalt"),
    "Heritage Damage": ("heritage", "monument", "historic", "historical"),
    "Heat Hazard": ("heatwave", "heat wave", "extreme heat", "heat hazard", "temperature", "melting", "dangerous temperatures", "unbearable", "full sun", "storing heat", "burns"),
    "Drain Blockage": ("drain blockage", "blocked drain", "drain blocked", "drain is blocked", "stormwater drain", "construction debris", "draining directly", "clogged drain", "drainage", "sewer"),
}

URGENT_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
    "hospitalised",
)


def _contains_keyword(description: str, keyword: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", description) is not None


def _classify_category(description: str) -> tuple[str, str]:
    matches = {
        category: [keyword for keyword in keywords if _contains_keyword(description, keyword)]
        for category, keywords in CATEGORIES.items()
    }
    matches = {category: keywords for category, keywords in matches.items() if keywords}

    if not matches:
        return "Other", "No allowed category keyword was found in the description."

    highest_score = max(
        (max(len(keyword) for keyword in keywords), len(keywords))
        for keywords in matches.values()
    )
    top_categories = [
        category
        for category, keywords in matches.items()
        if (max(len(keyword) for keyword in keywords), len(keywords)) == highest_score
    ]
    if len(top_categories) != 1:
        evidence = ", ".join(
            f'"{keyword}"'
            for category in top_categories
            for keyword in matches[category]
        )
        return "Other", f"The description contains equally strong evidence: {evidence}."

    category = top_categories[0]
    evidence = ", ".join(f'"{keyword}"' for keyword in matches[category])
    return category, f"The description mentions {evidence}, indicating {category}."


def classify_complaint(row: dict) -> dict:
    """Classify one complaint row using the fixed UC-0A taxonomy."""
    if not isinstance(row, dict):
        row = {}

    complaint_id = row.get("complaint_id", "")
    raw_description = row.get("description", "")
    description = raw_description.strip() if isinstance(raw_description, str) else ""
    normalized_description = description.casefold()

    is_urgent = any(
        _contains_keyword(normalized_description, keyword) for keyword in URGENT_KEYWORDS
    )
    priority = "Urgent" if is_urgent else "Standard"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "The complaint description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    category, reason = _classify_category(normalized_description)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if category == "Other" else "",
    }

def batch_classify(input_path: str, output_path: str):
    """Classify every input CSV row and write a result row for each one."""
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, "r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_fields)
            writer.writeheader()
            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as error:
                    result = {
                        "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"The row could not be classified: {type(error).__name__}.",
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
