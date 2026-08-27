"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": [r"pothole", r"potholes", r"tyre damage", r"tyre blowout"],
    "Flooding": [r"flood", r"flooded", r"flooding", r"waterlogged", r"submerged", r"draining.*road", r"rainwater"],
    "Streetlight": [r"streetlight", r"lights out", r"light out", r"flickering light", r"dark at night", r"unlit", r"darkness", r"wiring theft"],
    "Waste": [r"garbage", r"waste", r"overflowing bin", r"trash", r"rubbish", r"dead animal", r"bins overflowing"],
    "Noise": [r"noise", r"music", r"loud", r"blaring", r"midnight", r"past midnight", r"drilling", r"band playing", r"idling", r"amplifiers"],
    "Road Damage": [r"cracked", r"sinking", r"road surface", r"road broken", r"upturned", r"broken.*tile", r"footpath", r"collapsed", r"crater", r"subsided", r"buckled", r"paving"],
    "Heritage Damage": [r"heritage", r"old city", r"historic", r"cobblestone", r"heritage zone", r"heritage stone"],
    "Heat Hazard": [r"heat", r"heatwave", r"extreme heat", r"sunstroke", r"melting", r"temperature", r"burns on contact", r"exposed to.*sun", r"44°C", r"45°C", r"52°C"],
    "Drain Blockage": [r"drain blocked", r"blocked drain", r"manhole", r"sewer", r"drainage", r"drain.*blocked", r"stormwater drain", r"blocked with"],
}

FLAG_AMBIGUOUS = [
    r"mixed.*issue",
    r"multiple.*problem",
]


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    location = (row.get("location") or "").strip()
    ward = (row.get("ward") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    text = (description + " " + location + " " + ward).lower()

    category = _detect_category(text, description)
    priority = _detect_priority(description.lower())
    reason = _generate_reason(description, category)
    flag = ""

    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _detect_category(text: str, description: str) -> str | None:
    desc_lower = description.lower()
    for category, patterns in CATEGORY_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                return category
    for category, patterns in CATEGORY_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return category
    return None


def _detect_priority(text_lower: str) -> str:
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text_lower:
            return "Urgent"
    return "Standard"


def _generate_reason(description: str, category: str | None) -> str:
    if not description:
        return "Description missing — cannot classify."

    desc_lower = description.lower()
    phrases = []

    if category and category in CATEGORY_KEYWORDS:
        for pattern in CATEGORY_KEYWORDS[category]:
            match = re.search(pattern, desc_lower)
            if match:
                phrases.append(match.group(0))

    if not phrases:
        words = description.split()
        if len(words) > 3:
            phrases.append(" ".join(words[:4]))
        else:
            phrases.append(description)

    cited = phrases[0] if phrases else description[:40]

    if category:
        return f"Description mentions \"{cited}\" — classified as {category}."
    return f"Description mentions \"{cited}\" but category is unclear."


def batch_classify(input_path: str, output_path: str):
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row processing failed.",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if not results:
        print("Warning: No results to write.")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
