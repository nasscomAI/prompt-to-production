"""
UC-0A — Complaint Classifier
Keyword-based classification following RICE enforcement rules.
"""
import argparse
import csv
import os
import re

SEVERITY_KEYWORDS = [
    "injury", "injured", "injuries",
    "child", "children",
    "school", "hospital", "ambulance",
    "fire", "hazard", "hazardous",
    "fell", "collapse", "collapsed",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "crater"]),
    ("Flooding", ["flooded", "flood", "waterlogged", "knee deep", "stranded", "inaccessible"]),
    ("Drain Blockage", ["drain blocked", "drainage", "blocked drain", "draining", "drain"]),
    ("Streetlight", ["streetlight", "lights out", "light out", "flickering", "sparking",
                      "unlit", "darkness", "lamp post", "substation", "lamp"]),
    ("Waste", ["garbage", "waste", "overflowing", "bins overflow", "dead animal",
               "dumped", "refuse", "bin overflow", "not removed"]),
    ("Noise", ["music", "noise", "loud", "amplifier", "band", "wedding", "drilling"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "subsidence", "subsided",
                      "footpath", "manhole", "road damaged", "paving", "cobblestone",
                      "buckled", "broken", "upturned", "tiles broken", "road collapsed",
                      "collapsed"]),
    ("Heritage Damage", ["heritage", "historic", "ancient", "heritage zone",
                          "heritage street", "heritage stone", "heritage precinct",
                          "heritage area", "heritage lamp"]),
    ("Heat Hazard", ["temperature", "heat", "melting", "burning", "unbearable",
                      "°C", "heatwave", "storing heat", "bubbling"]),
]

AMBIGUITY_PATTERNS = [
    (r"heritage.*(light|lamp)|(light|lamp).*heritage", ["Heritage Damage", "Streetlight"]),
    (r"heritage.*(noise|music|amplifier|band|wedding)", ["Heritage Damage", "Noise"]),
    (r"(noise|music|amplifier|band|wedding).*heritage", ["Noise", "Heritage Damage"]),
    (r"heritage.*(waste|garbage)|(waste|garbage).*heritage", ["Heritage Damage", "Waste"]),
    (r"flooded.*drain.*blocked|drain.*blocked.*flooded", ["Flooding", "Drain Blockage"]),
]


def normalize(text: str) -> str:
    return text.lower().replace("-", " ").replace("/", " ")


def determine_priority(desc: str) -> str:
    desc_norm = normalize(desc)
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", desc_norm):
            return "Urgent"
    return "Standard"


def determine_category(desc: str) -> tuple:
    """Returns (category, flag) where flag is 'NEEDS_REVIEW' or ''."""
    desc_norm = normalize(desc)

    # Check for ambiguity patterns first
    for pattern, candidates in AMBIGUITY_PATTERNS:
        if re.search(pattern, desc_norm):
            return (candidates[0], "NEEDS_REVIEW")

    # Score each category using substring matching
    best_cat = "Other"
    best_score = 0
    for cat, keywords in CATEGORY_RULES:
        score = sum(1 for kw in keywords if kw in desc_norm)
        if score > best_score:
            best_score = score
            best_cat = cat

    if best_score == 0:
        return ("Other", "NEEDS_REVIEW")

    return (best_cat, "")


def build_reason(desc: str, category: str, priority: str, flag: str) -> str:
    desc_norm = normalize(desc)
    if flag == "NEEDS_REVIEW":
        return f"Description: '{desc[:80]}...' — category ambiguous, needs manual review."
    cited = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_norm:
            cited.append(f"'{kw}'")
    if category.lower() in desc_norm:
        cited.append(f"'{category.lower()}'")
    else:
        for cat, keywords in CATEGORY_RULES:
            if cat == category:
                for kw in keywords:
                    if kw in desc_norm:
                        cited.append(f"'{kw}'")
                        break
                break
    if cited:
        return f"Keywords found: {', '.join(cited[:3])} in description."
    return f"Classified as {category} based on description content."


def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "")
    category, flag = determine_category(desc)
    priority = determine_priority(desc)
    reason = build_reason(desc, category, priority, flag)
    return {
        "complaint_id": row.get("complaint_id", ""),
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
            rows.append(row)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "complaint_id", "category", "priority", "reason", "flag"
        ])
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {e}",
                    "flag": "NEEDS_REVIEW",
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
