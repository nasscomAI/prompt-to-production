"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
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

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "waterlogged", "waterlogging", "stranded", "underpass"],
    "Streetlight": ["streetlight", "streetlights", "lights out", "flickering", "sparking", "dark at night", "dark"],
    "Waste": ["garbage", "waste", "bins", "dead animal", "overflowing", "smell"],
    "Noise": ["noise", "music", "drilling", "idling", "past midnight", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "collapsed", "crater", "tiles broken", "upturned", "manhole cover", "footpath"],
    "Heritage Damage": ["heritage wall", "monument", "historic", "heritage structure", "vandal", "defaced"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "dehydration", "no shade", "extreme temperature"],
    "Drain Blockage": ["drain blocked", "drainage blocked", "drain clogged", "stormwater drain", "manhole blocked", "debris"],
}


def _build_text(row: dict) -> str:
    description = (row.get("description") or "").strip()
    location = (row.get("location") or "").strip()
    return f"{description} {location}".lower()


def _score_categories(text: str) -> dict:
    scores = {category: 0 for category in ALLOWED_CATEGORIES if category != "Other"}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] += 1
    return scores


def _extract_evidence(text: str, category: str) -> list:
    evidence = []
    for keyword in CATEGORY_KEYWORDS.get(category, []):
        if keyword in text:
            evidence.append(keyword)
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text and keyword not in evidence:
            evidence.append(keyword)
    return evidence[:3]


def _pick_category(scores: dict) -> tuple:
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_category, best_score = ranked[0]
    tied_top = [category for category, score in ranked if score == best_score and score > 0]

    if best_score == 0:
        return "Other", True

    if len(tied_top) > 1:
        return tied_top[0], True

    return best_category, False


def _pick_priority(text: str) -> str:
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            return "Urgent"
    return "Standard"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A schema using deterministic keyword rules.
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    text = _build_text(row)

    scores = _score_categories(text)
    category, ambiguous = _pick_category(scores)
    priority = _pick_priority(text)
    evidence = _extract_evidence(text, category)

    if evidence:
        reason = f"Classified as {category} based on words: {', '.join([repr(word) for word in evidence])}."
    else:
        reason = "No clear category keywords found in description, so marked as Other."

    flag = "NEEDS_REVIEW" if ambiguous else ""

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Detected an invalid category during processing, so fell back to Other."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Reads input CSV, classifies each row, and writes stable output.
    Does not crash on malformed rows; emits review-flagged fallback rows instead.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                complaint_id = (row.get("complaint_id") or "").strip() or f"ROW-{index}"
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed due to row error: {str(exc)}.",
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
