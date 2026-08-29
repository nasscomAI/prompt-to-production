"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {"Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"}

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooding"],
    "Streetlight": ["streetlight", "street light", "lamppost", "lamp", "unlit", "lights", "darkness"],
    "Waste": ["waste", "trash", "garbage", "litter", "rubbish", "dump"],
    "Noise": ["noise", "loud", "siren", "clamor", "music", "band", "amplifier"],
    "Road Damage": ["road damage", "crater", "degradation", "rut"],
    "Heritage Damage": ["heritage", "historic", "monument", "landmark", "statue"],
    "Heat Hazard": ["heat", "hot", "temperature", "melting", "bubbling", "°c"],
    "Drain Blockage": ["drain", "blockage", "blocked", "clog", "backflow"],
}

MINOR_WORDS = ["minor", "cosmetic", "slight", "small", "tiny", "aesthetic"]


def _find_category(description: str) -> tuple[str, bool]:
    desc_lower = description.lower()
    best_match = None
    best_score = 0
    for cat, words in CATEGORY_KEYWORDS.items():
        score = sum(1 for w in words if w in desc_lower)
        if score > best_score:
            best_score = score
            best_match = cat
    if best_match and best_score > 0:
        return best_match, True
    return "Other", False


def _contains_urgent(description: str) -> bool:
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in URGENT_KEYWORDS)


def _extract_reason(description: str, category: str) -> str:
    desc_lower = description.lower()
    cat_words = CATEGORY_KEYWORDS.get(category, [])
    for word in description.split():
        clean = re.sub(r'[^a-zA-Z]', '', word).lower()
        for kw in cat_words:
            if clean == kw or kw in clean or clean in kw:
                return f'Description mentions "{word}" indicating {category.lower()}.'
    for word in description.split():
        clean = re.sub(r'[^a-zA-Z]', '', word).lower()
        if clean:
            return f'Description mentions "{word}" indicating {category.lower()}.'
    return f'Description indicates {category.lower()}.'


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").strip() if row.get("description") else ""
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, confident = _find_category(description)

    if not confident:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    if _contains_urgent(description):
        priority = "Urgent"
    elif any(w in description.lower() for w in MINOR_WORDS):
        priority = "Low"
    else:
        priority = "Standard"

    reason = _extract_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "No description provided.",
                "flag": "NEEDS_REVIEW",
            })

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")