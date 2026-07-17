"""
UC-0A — Complaint Classifier
"""

import argparse
import csv
import re
from typing import Dict, List, Set, Tuple

ALLOWED_CATEGORIES: List[str] = [
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
ALLOWED_PRIORITIES: Set[str] = {"Urgent", "Standard", "Low"}
SEVERITY_KEYWORDS: List[str] = [
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

CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogging", "water logged", "water-logged", "inundat"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamp", "dark road", "no light"],
    "Waste": ["garbage", "trash", "waste", "dump", "litter", "bin overflow", "overflowing bin"],
    "Noise": ["noise", "loud", "blaring", "horn", "speaker", "construction noise"],
    "Road Damage": ["road damage", "broken road", "cracked road", "damaged road", "road surface", "uneven road"],
    "Heritage Damage": ["heritage", "monument", "historic", "protected structure"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "no shade", "heatstroke", "hot pavement"],
    "Drain Blockage": ["drain", "sewer", "sewage", "clog", "blocked", "choked", "manhole"],
}

_DESCRIPTION_KEYS: Tuple[str, ...] = ("description", "complaint", "details", "message", "text")


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_description(row: dict) -> str:
    for key in _DESCRIPTION_KEYS:
        value = row.get(key)
        if value is not None and str(value).strip():
            return _normalize_space(str(value))
    return ""


def _find_severity_hits(text_lc: str) -> List[str]:
    hits = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", text_lc):
            hits.append(kw)
    return hits


def _category_hits(text_lc: str) -> Dict[str, List[str]]:
    hits: Dict[str, List[str]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        matched = []
        for p in patterns:
            if p in text_lc:
                matched.append(p)
        if matched:
            hits[category] = matched
    return hits


def _one_sentence_reason(category: str, evidence: List[str], fallback: str) -> str:
    if evidence:
        quoted = ", ".join(f"'{e}'" for e in sorted(set(evidence)))
        return f"Classified as {category} because the description includes {quoted}."
    return fallback


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = _extract_description(row)
    text_lc = description.lower()

    severity_hits = _find_severity_hits(text_lc)
    priority = "Urgent" if severity_hits else "Standard"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "Classified as Other because the description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    cat_hits = _category_hits(text_lc)
    if not cat_hits:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classified as Other because the description does not clearly match any allowed category."
    else:
        max_score = max(len(v) for v in cat_hits.values())
        top_categories = sorted([c for c, v in cat_hits.items() if len(v) == max_score])
        category = top_categories[0]
        ambiguous = len(top_categories) > 1
        flag = "NEEDS_REVIEW" if ambiguous else ""

        evidence = list(cat_hits.get(category, []))
        if severity_hits:
            evidence.extend(severity_hits)
        reason = _one_sentence_reason(
            category,
            evidence,
            f"Classified as {category} based on complaint wording.",
        )

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classified as Other because the predicted category was outside the allowed schema."

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    if not reason.endswith("."):
        reason = reason.rstrip(" .") + "."

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
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception:
                complaint_id = str(row.get("complaint_id", "")).strip()
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classified as Other because the row could not be processed reliably.",
                    "flag": "NEEDS_REVIEW",
                }

            if classified.get("category") not in ALLOWED_CATEGORIES:
                classified["category"] = "Other"
                classified["flag"] = "NEEDS_REVIEW"
            if classified.get("priority") not in ALLOWED_PRIORITIES:
                classified["priority"] = "Standard"
            if not str(classified.get("reason", "")).strip():
                classified["reason"] = "Classified as Other because the complaint lacked enough evidence to justify a category."
            if classified.get("flag") not in {"", "NEEDS_REVIEW"}:
                classified["flag"] = "NEEDS_REVIEW"

            writer.writerow({k: classified.get(k, "") for k in output_fields})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
