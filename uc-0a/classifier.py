"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_PATTERNS = [
    (["pothole", "crater", "dip in road", "dip in the road"], "Pothole"),
    (["flood", "flooding", "waterlogged", "water logging", "stagnant water", "water accumulation"], "Flooding"),
    (["streetlight", "street light", "street lamp", "burnt.?out bulb", "light.*not working", "no light"], "Streetlight"),
    (["garbage", "waste", "trash", "rubbish", "debris", "litter", "dump", "refuse", "uncollected"], "Waste"),
    (["noise", "loud", "honking", "disturbance", "noisy", "racket"], "Noise"),
    (["road damage", "damaged road", "broken road", "cracked road", "uneven road", "deteriorated road", "large cracks", "road.*damage", "road.*crack", "road.*broken"], "Road Damage"),
    (["heritage", "monument", "historical", "ancient", "archaeological", "listed building"], "Heritage Damage"),
    (["heat", "temperature", "hot", "heatwave", "heat wave", "scorching"], "Heat Hazard"),
    (["drain", "blockage", "clogged", "sewer", "blocked drain", "drain.*block"], "Drain Blockage"),
]

TRIVIAL_PATTERN = re.compile(r"single\s+burnt[- ]?out\s+bulb", re.IGNORECASE)


def _extract_matched_words(description: str, desc_lower: str, category: str) -> list[str]:
    matched = []
    for patterns, cat in CATEGORY_PATTERNS:
        if cat == category:
            for pat in patterns:
                m = re.search(re.escape(pat) if not any(c in pat for c in ".?*+^${}()|[]\\") else pat, desc_lower)
                if m:
                    s, e = m.span()
                    word = description[s:e].strip()
                    if word:
                        matched.append(word)
    return list(dict.fromkeys(matched))


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category = None
    for patterns, cat in CATEGORY_PATTERNS:
        for pat in patterns:
            if re.search(pat, desc_lower):
                category = cat
                break
        if category:
            break

    if category is None:
        category = "Other"

    is_trivial = bool(TRIVIAL_PATTERN.search(description))
    if is_trivial:
        priority = "Low"
    elif any(kw in desc_lower for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    matched_words = _extract_matched_words(description, desc_lower, category)
    if matched_words:
        cited = "', '".join(matched_words[:3])
        reason = f"Description mentions '{cited}' indicating {category.lower()} issue."
    elif category == "Other":
        words = description.split()[:5]
        cited = " ".join(words)
        reason = f"Description '{cited}...' does not clearly match any known category."
    else:
        cited = description[:80]
        reason = f"Description '{cited}' classified as {category.lower()}."

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                cid = row.get("complaint_id", "").strip()
                if not cid:
                    print(f"Warning: Row {i} missing complaint_id, skipping")
                    continue
                result = classify_complaint(row)
                rows.append(result)
            except Exception as e:
                print(f"Warning: Row {i} failed ({e}), writing as NEEDS_REVIEW")
                rows.append({
                    "complaint_id": row.get("complaint_id", f"row_{i}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Malformed row — could not process",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
