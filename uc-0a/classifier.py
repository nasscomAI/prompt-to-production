import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlog", "submerged", "waterlogged", "rainwater"],
    "Streetlight": ["streetlight", "street light", "lamp", "unlit", "darkness", "substation", "lights out", "sparking"],
    "Waste": ["garbage", "waste", "trash", "dump", "litter", "debris", "rubbish", "overflowing", "carcass", "dead animal"],
    "Noise": ["noise", "loud", "honk", "disturbance", "noisy", "music", "band", "amplifier", "drilling", "idling", "engine"],
    "Road Damage": ["road damage", "damaged road", "broken road", "cracked road", "road surface", "buckled", "subsided", "subsidence", "footpath", "manhole"],
    "Heritage Damage": ["heritage", "historic", "monument", "historical", "heritage site", "heritage zone", "heritage precinct"],
    "Heat Hazard": ["heat", "hot", "sun", "temperature", "heatwave", "melting", "bubbling"],
    "Drain Blockage": ["drain", "drainage", "blockage", "blocked", "sewage", "clogged", "gutter", "draining"],
}


def _get_words(text: str) -> set:
    return set(re.findall(r"[a-zA-Z]+", text.lower()))


def _has_any_word_match(text: str, keywords: list) -> bool:
    words = _get_words(text)
    text_lower = text.lower()
    for kw in keywords:
        kw_parts = kw.split()
        if len(kw_parts) == 1:
            base = kw_parts[0]
            if base in words:
                return True
            if base + "s" in words:
                return True
            if base + "es" in words:
                return True
            if base + "ing" in words:
                return True
            if base + "ed" in words:
                return True
        else:
            if kw.lower() in text_lower:
                return True
    return False


def _find_category(desc: str) -> tuple:
    matches = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if _has_any_word_match(desc, keywords):
            matches.append(cat)
    if "Drain Blockage" in matches and "Flooding" in matches:
        matches = [m for m in matches if m != "Drain Blockage"]
    if "Drain Blockage" in matches and "Waste" in matches:
        matches = [m for m in matches if m != "Waste"]
    if "Pothole" in matches and "Flooding" in matches:
        matches = [m for m in matches if m != "Flooding"]
    if len(matches) == 1:
        return matches[0], ""
    if len(matches) > 1:
        return "Other", "NEEDS_REVIEW"
    if "drain" in _get_words(desc):
        return "Drain Blockage", ""
    return "Other", "NEEDS_REVIEW"


def _build_reason(desc: str, category: str, priority: str) -> str:
    cited = []
    desc_lower = desc.lower()
    if category != "Other":
        for kw in CATEGORY_KEYWORDS.get(category, []):
            if kw.lower() in desc_lower:
                cited.append(kw)
                break
    if priority == "Urgent":
        for kw in URGENT_KEYWORDS:
            if kw.lower() in desc_lower:
                cited.append(kw)
                break
    if not cited:
        words = [w for w in desc.split() if len(w) > 3]
        if words:
            cited.append(words[-1].strip(".,!?;:"))
        else:
            cited.append(desc.split()[-1].strip(".,!?;:") if desc.split() else "")
    return "Cited: " + ", ".join(cited) + " from description."


def classify_complaint(row: dict) -> dict:
    if "complaint_id" not in row or "description" not in row:
        raise ValueError("Row must contain complaint_id and description")
    desc = (row.get("description") or "").strip()
    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description provided.",
            "flag": "NEEDS_REVIEW",
        }
    category, flag = _find_category(desc)
    priority = "Urgent" if _has_any_word_match(desc, URGENT_KEYWORDS) else "Standard"
    reason = _build_reason(desc, category, priority)
    return {
        "complaint_id": row["complaint_id"],
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "complaint_id" not in row or "description" not in row:
                continue
            rows.append(row)
    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            continue
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
