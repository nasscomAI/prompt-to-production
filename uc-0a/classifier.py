"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import logging

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

TAXONOMY_RULES = [
    ("Pothole", ["pothole", "crater", "hole in road", "hole in the road"]),
    ("Flooding", ["flood", "stagnant water", "waterlog", "water log", "submerged", "water rising"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "light not working", "dark street"]),
    ("Waste", ["garbage", "waste", "trash", "rubbish", "debris", "litter", "dump", "solid waste"]),
    ("Noise", ["noise", "loud", "disturbance", "honking", "construction sound"]),
    ("Road Damage", ["road damage", "broken road", "cracked road", "damaged road", "uneven road", "bumpy road"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "archaeological", "heritage site"]),
    ("Heat Hazard", ["heat", "heat wave", "heatstroke", "heat hazard", "extreme temperature"]),
    ("Drain Blockage", ["drain", "blockage", "clogged", "choked drain", "gutter", "sewage", "drain block"]),
]

logger = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    return text.lower().strip()


def _find_matching_keyword(text: str, keywords: list[str]) -> str | None:
    lowered = _normalize(text)
    for kw in keywords:
        if kw in lowered:
            return kw
    return None


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = []
    matched_cited_keywords = []
    for category, keywords in TAXONOMY_RULES:
        kw = _find_matching_keyword(description, keywords)
        if kw:
            matched_categories.append(category)
            matched_cited_keywords.append(kw)

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        cited = matched_cited_keywords[0]
        reason = f"The complaint mentions '{cited}' indicating {category}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if matched_cited_keywords:
            cited = ", ".join(matched_cited_keywords)
            reason = f"The complaint mentions '{cited}' which maps to multiple categories, requiring review."
        else:
            desc_words = description.strip().split()
            snippet = " ".join(desc_words[:8])
            reason = f"The complaint mentions '{snippet}' which does not clearly map to any category, requiring review."

    severity_hit = _find_matching_keyword(description, SEVERITY_KEYWORDS)
    if severity_hit:
        priority = "Urgent"
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                result["description"] = row.get("description", "")
                rows.append(result)
            except Exception:
                logger.error("Skipping row %d due to error", i)

    if not rows:
        logger.warning("No rows classified; writing empty output.")
        rows = [{"complaint_id": "", "description": "", "category": "Other", "priority": "Low", "reason": "No data processed.", "flag": "NEEDS_REVIEW"}]

    fieldnames = ["complaint_id", "description", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
