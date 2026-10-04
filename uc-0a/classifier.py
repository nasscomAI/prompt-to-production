"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole"],
    "Flooding": [r"\bflood", r"\bwaterlog"],
    "Streetlight": [r"\bstreetlight", r"\bstreet\s*light", r"\blights?\s*out", r"\bflicker", r"\bunlit"],
    "Waste": [r"\bgarbage", r"\bwaste\b", r"\bbins?\b", r"\bdead\s+animal", r"\bbulk\s+waste", r"\bdumping", r"\boverflow"],
    "Noise": [r"\bnoise", r"\bmusic", r"\bloud", r"\bhonking", r"\bdrilling", r"\bidling", r"\bband"],
    "Road Damage": [r"\bmanhole", r"\bfootpath", r"\bcracked", r"\bsinking", r"\bcollaps", r"\bbuckled", r"\bsubsid", r"\bbench", r"\bcobblestone"],
    "Heritage Damage": [r"\bheritage"],
    "Heat Hazard": [r"\bheat\b", r"\btemperature", r"\bheatwave", r"\b\d+°"],
    "Drain Blockage": [r"\bblockage", r"\bsewer", r"\bdrain.*?blocked", r"\bblocked.*?drain"],
}

AMBIGUOUS_PAIRS = [
    ("Heritage Damage", "Streetlight"),
]


def classify_complaint(row: dict) -> dict:
    desc = (row.get("description") or "").strip()
    cid = row.get("complaint_id", "")

    if not desc:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()
    category, flag = _determine_category(desc_lower)
    priority = _determine_priority(desc_lower)
    reason = _extract_reason(desc, desc_lower, category)

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _determine_category(desc_lower):
    scores = {}
    first_positions = {}

    for cat, patterns in CATEGORY_PATTERNS.items():
        score = 0
        first_pos = len(desc_lower)
        for p in patterns:
            for m in re.finditer(p, desc_lower):
                score += 1
                if m.start() < first_pos:
                    first_pos = m.start()
        if score > 0:
            scores[cat] = score
            first_positions[cat] = first_pos

    if not scores:
        return "Other", "NEEDS_REVIEW"

    max_score = max(scores.values())
    top_cats = [c for c, s in scores.items() if s == max_score]

    if len(top_cats) == 1:
        return top_cats[0], ""

    for a, b in AMBIGUOUS_PAIRS:
        if a in top_cats and b in top_cats:
            return "Other", "NEEDS_REVIEW"

    min_pos = min(first_positions[c] for c in top_cats)
    earliest = [c for c in top_cats if first_positions[c] == min_pos]

    if len(earliest) == 1:
        return earliest[0], ""

    return "Other", "NEEDS_REVIEW"


def _determine_priority(desc_lower):
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw), desc_lower):
            return "Urgent"
    return "Standard"


def _extract_reason(desc, desc_lower, category):
    if category == "Other":
        sents = re.split(r'(?<=[.!])\s+', desc)
        return sents[0].strip() if sents else desc[:100]

    patterns = CATEGORY_PATTERNS.get(category, [])
    matched_text = None
    match_pos = len(desc_lower)

    for p in patterns:
        for m in re.finditer(p, desc_lower):
            if m.start() < match_pos:
                match_pos = m.start()
                matched_text = m.group()

    sents = re.split(r'(?<=[.!])\s+', desc)
    for s in sents:
        if matched_text and matched_text in s.lower():
            return s.strip()

    return sents[0].strip() if sents else desc[:100]


def batch_classify(input_path: str, output_path: str):
    rows = []
    try:
        with open(input_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        raise

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW"
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
