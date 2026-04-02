import argparse
import csv
from typing import Dict, Tuple

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

CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "crater",
        "road hole",
    ],
    "Flooding": [
        "flood",
        "flooding",
        "waterlogged",
        "water logging",
        "water-logging",
        "standing water",
        "submerged",
        "rainwater",
        "water through road",
        "water on road",
        "road flooded",
        "water entering road",
        "main road flooded",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "light not working",
        "lights not working",
        "dark road",
        "dark street",
        "lamp post",
        "lamp",
        "no lights",
        "street in darkness",
        "area is dark",
    ],
    "Waste": [
        "garbage",
        "trash",
        "waste",
        "dump",
        "dumping",
        "overflowing bin",
        "overflowing garbage",
        "rubbish",
        "litter",
    ],
    "Noise": [
        "noise",
        "loudspeaker",
        "speaker",
        "dj",
        "horn",
        "honking",
        "construction noise",
        "loud music",
        "sound pollution",
        "drilling",
        "drill",
        "idling",
        "truck idling",
        "engine on",
        "engines on",
        "delivery trucks",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road cracked",
        "uneven road",
        "road sinking",
        "collapsed road",
        "road surface damaged",
        "caved road",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "statue",
        "historic wall",
        "historic structure",
        "old building",
        "protected structure",
    ],
    "Heat Hazard": [
        "heat",
        "extreme heat",
        "heatwave",
        "no shade",
        "sun exposure",
        "hot pavement",
        "burning surface",
    ],
    "Drain Blockage": [
        "drain",
        "blocked drain",
        "choked drain",
        "sewage",
        "manhole",
        "clogged drain",
        "drain blockage",
        "overflowing drain",
        "gutter",
    ],
}


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def find_description_field(row: Dict[str, str]) -> str:
    possible_fields = [
        "description",
        "complaint",
        "complaint_text",
        "issue",
        "details",
        "text",
        "body",
    ]

    for field in possible_fields:
        if field in row and str(row[field]).strip():
            return str(row[field]).strip()

    best_value = ""
    for key, value in row.items():
        if key is None:
            continue
        key_l = str(key).strip().lower()
        if "id" in key_l:
            continue
        value_str = str(value).strip()
        if len(value_str) > len(best_value):
            best_value = value_str

    return best_value


def find_complaint_id(row: Dict[str, str]) -> str:
    possible_fields = [
        "complaint_id",
        "id",
        "ticket_id",
        "case_id",
        "reference_id",
    ]

    for field in possible_fields:
        if field in row and str(row[field]).strip():
            return str(row[field]).strip()

    for value in row.values():
        if str(value).strip():
            return str(value).strip()

    return ""


def detect_category(description: str) -> Tuple[str, str]:
    text = normalize_text(description)

    # HARD RULES FIRST (more reliable than keyword lists)

    # Noise (construction / drilling / vehicles)
    if any(word in text for word in ["drilling", "drill", "idling", "engine", "truck", "noise"]):
        return "Noise", "drilling" if "drilling" in text else "noise"

    # Flooding (rainwater / flow)
    if any(word in text for word in ["rainwater", "water", "flood", "waterlogged", "submerged"]):
        if "road" in text or "main road" in text:
            return "Flooding", "rainwater" if "rainwater" in text else "water"

    # Drain blockage
    if "drain" in text or "sewage" in text:
        return "Drain Blockage", "drain"

    # Pothole
    if "pothole" in text or "crater" in text:
        return "Pothole", "pothole" if "pothole" in text else "crater"

    # Streetlight
    if any(word in text for word in ["streetlight", "lamp", "dark", "no lights"]):
        return "Streetlight", "streetlight"

    # Waste
    if any(word in text for word in ["garbage", "waste", "trash", "dump"]):
        return "Waste", "waste"

    # Road damage
    if any(word in text for word in ["cracked", "broken road", "road damage", "collapsed road"]):
        return "Road Damage", "road damage"

    # Heritage
    if "heritage" in text or "monument" in text:
        return "Heritage Damage", "heritage"

    # Heat hazard
    if "heat" in text or "heatwave" in text:
        return "Heat Hazard", "heat"

    return "Other", ""


def detect_priority(description: str) -> Tuple[str, str]:
    text = normalize_text(description)

    for kw in SEVERITY_KEYWORDS:
        if kw in text:
            return "Urgent", kw

    low_keywords = ["minor", "slight", "small", "occasionally", "sometimes"]
    for kw in low_keywords:
        if kw in text:
            return "Low", kw

    return "Standard", ""


def build_reason(
    description: str,
    category: str,
    category_keyword: str,
    priority: str,
    priority_keyword: str,
) -> str:
    if not description.strip():
        return "Description is missing or unusable, so the complaint was marked Other and needs review."

    if category == "Other":
        return "The description does not clearly match any allowed category based on the given text."

    if priority == "Urgent" and category_keyword and priority_keyword:
        return (
            f"Classified as {category} because the description includes '{category_keyword}', "
            f"and marked Urgent because it includes '{priority_keyword}'."
        )

    if category_keyword:
        return f"Classified as {category} because the description includes '{category_keyword}'."

    return f"Classified as {category} based on the complaint description."


def classify_complaint(row: dict) -> dict:
    complaint_id = find_complaint_id(row)
    description = find_description_field(row)

    if not normalize_text(description):
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or unusable, so the complaint could not be classified.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_keyword = detect_category(description)
    priority, priority_keyword = detect_priority(description)

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = build_reason(description, category, category_keyword, priority, priority_keyword)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        priority = "Standard"
        flag = "NEEDS_REVIEW"
        reason = "Detected category was invalid, so the complaint was reassigned to Other and flagged for review."

    if priority not in ["Urgent", "Standard", "Low"]:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                complaint_id = ""
                try:
                    complaint_id = find_complaint_id(row)
                except Exception:
                    complaint_id = ""

                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row could not be safely classified due to processing error: {str(e)}.",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")