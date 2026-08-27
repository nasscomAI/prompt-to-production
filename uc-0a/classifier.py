"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re


def _clean(text: str) -> str:
    return text.strip().lower()


def _classify_category(desc: str) -> tuple:
    """
    Return (category, flag) based on description keywords.
    flag is 'NEEDS_REVIEW' if genuinely ambiguous, else ''.
    """
    d = _clean(desc)

    categories = []

    # Pothole
    if re.search(r'\bpotholes?\b', d) or re.search(r'tyre (damage|blowout)', d) or re.search(r'\bcrater\b', d):
        categories.append("Pothole")

    # Flooding
    if re.search(r'\bflood(ed|ing|s)?\b', d) or re.search(r'underpass flood', d) or \
       re.search(r'standing in water', d) or re.search(r'flooding risk', d) or \
       re.search(r'\brainwater\b', d):
        categories.append("Flooding")

    # Streetlight
    if re.search(r'streetlight', d) or re.search(r'lights? out', d) or \
       re.search(r'\bunlit\b', d) or re.search(r'\bdarkness\b', d) or \
       re.search(r'\bsparking\b', d):
        categories.append("Streetlight")

    # Waste
    if re.search(r'\b(garbage|waste|trash)\b', d) or \
       re.search(r'dead animal', d) or re.search(r'\bwaste bins?\b', d):
        categories.append("Waste")

    # Noise
    if re.search(r'\bmusic\b', d) or re.search(r'\bnoise\b', d) or \
       re.search(r'\bdrilling\b', d) or re.search(r'\bamplifiers?\b', d) or \
       re.search(r'\bband\b', d) or re.search(r'\bidling\b', d):
        categories.append("Noise")

    # Road Damage
    if re.search(r'road (surface|cracked|sinking|buckled|collapsed|subsided|subsidence)', d) or \
       re.search(r'footpath.*(broken|sinking|cracked|upturned)', d) or \
       re.search(r'\bmanhole cover missing\b', d):
        categories.append("Road Damage")

    # Heritage Damage
    if re.search(r'heritage', d):
        categories.append("Heritage Damage")

    # Heat Hazard
    if re.search(r'\b(heat|temperatures?|melting|heatwave|burns?)\b', d) and \
       not re.search(r'\bfire\b', d):
        categories.append("Heat Hazard")

    # Drain Blockage
    if re.search(r'drain (blocked|clogged)', d) or \
       re.search(r'stormwater drain', d):
        categories.append("Drain Blockage")

    # If only one category matched, use it
    if len(categories) == 1:
        return (categories[0], "")

    # If multiple matched, decide if genuinely ambiguous
    if len(categories) > 1:
        # Some combos are clear enough — pick the dominant one
        # Flooding + Drain Blockage -> Flooding (drain blockage causes flooding)
        if "Flooding" in categories and "Drain Blockage" in categories:
            if re.search(r'\bflood', d):
                return ("Flooding", "")
        # Pothole + Flooding -> Pothole (pothole described as filling with rainwater)
        if "Pothole" in categories and "Flooding" in categories:
            return ("Pothole", "")
        # Road Damage + Pothole -> Pothole (pothole is a type of road damage)
        if "Pothole" in categories and "Road Damage" in categories:
            return ("Pothole", "")
        # Streetlight + Heritage -> Heritage Damage if heritage mentioned
        if "Streetlight" in categories and "Heritage Damage" in categories:
            return ("Heritage Damage", "")
        # Otherwise ambiguous
        return (categories[0], "NEEDS_REVIEW")

    # No category matched — try harder with edge cases
    # Paving broken/removed/upturned -> Road Damage
    if re.search(r'paving.*(broken|removed|upturned)', d) or re.search(r'upturned paving', d) or \
       re.search(r'road.*work', d):
        return ("Road Damage", "")

    # Heritage zone garbage -> Heritage Damage
    if re.search(r'heritage.*garbage|heritage.*waste', d):
        return ("Heritage Damage", "")

    # Heritage street with lights out -> Heritage Damage
    if re.search(r'heritage.*light', d):
        return ("Heritage Damage", "")

    # Electrical hazard -> Streetlight
    if re.search(r'electrical hazard', d):
        return ("Streetlight", "")

    # Bridge approach floods -> Flooding
    if re.search(r'bridge.*flood', d):
        return ("Flooding", "")

    # Gas leak -> Other (not in our categories cleanly)
    if re.search(r'gas leak', d):
        return ("Other", "")

    # Substation tripped, darkness -> Streetlight
    if re.search(r'substation tripped', d) or re.search(r'darkness', d):
        return ("Streetlight", "")

    # Construction debris -> Waste
    if re.search(r'construction debris', d):
        return ("Waste", "")

    # Road subsided -> Road Damage
    if re.search(r'road subsided', d):
        return ("Road Damage", "")

    # Heritage building exterior defaced -> Heritage Damage
    if re.search(r'heritage.*(building|residential|exterior)', d):
        return ("Heritage Damage", "")

    # BRT shelter roof glass broken -> Other
    if re.search(r'(bus )?shelter', d) or re.search(r'roof glass', d):
        return ("Other", "NEEDS_REVIEW")

    # Idling trucks/delivery vehicles -> Noise
    if re.search(r'\bidling\b', d):
        return ("Noise", "")

    # Public road draining / channeling water -> Flooding
    if re.search(r'draining (onto|into|across).*road', d) or re.search(r'channel.*rainwater', d):
        return ("Flooding", "NEEDS_REVIEW")

    # Bridge approach / road subsided — already handled above
    # Fall risk (trees) -> Other
    if re.search(r'\bfall risk\b', d):
        return ("Other", "NEEDS_REVIEW")

    # Last resort
    return ("Other", "NEEDS_REVIEW")


URGENT_KEYWORDS = [
    r'\binjury\b', r'\bchild\b', r'\bschool\b', r'\bhospital\b',
    r'\bambulance\b', r'\bfire\b', r'\bhazard\b', r'\bfell\b',
    r'\bcollaps(?:e|ed|ing)\b', r'\binjured\b', r'\bburns?\b',
]


def _classify_priority(desc: str) -> str:
    d = _clean(desc)
    for kw in URGENT_KEYWORDS:
        if re.search(kw, d):
            return "Urgent"
    return "Standard"


def _format_reason(desc: str, category: str, priority: str) -> str:
    d = desc.strip()
    words = d.split()
    # Extract a short relevant quote (up to ~15 words) from the description
    # that supports the classification
    if len(words) <= 20:
        quote = d
    else:
        quote = " ".join(words[:20]) + "..."

    return f"Description mentions: \"{quote}\" — classified as {category} with {priority} priority."


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    category, flag = _classify_category(description)
    priority = _classify_priority(description)
    reason = _format_reason(description, category, priority)

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Error processing: {e}",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
