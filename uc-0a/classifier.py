"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path


ALLOWED_CATEGORIES = {
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
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}
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

LOW_PRIORITY_HINTS = [
    "minor",
    "small",
    "dim",
    "flicker",
    "occasional",
    "sometimes",
    "not urgent",
    "when convenient",
]

TEXT_FIELD_CANDIDATES = [
    "description",
    "complaint",
    "complaint_text",
    "details",
    "issue",
    "message",
    "text",
    "remarks",
    "summary",
]

ID_FIELD_CANDIDATES = ["complaint_id", "id", "ticket_id", "case_id", "request_id"]

CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "pit", "crater", "hole in road", "road hole"],
    "Flooding": ["flood", "flooding", "waterlogging", "water logged", "inundat", "water on road"],
    "Streetlight": ["streetlight", "street light", "light not working", "dark street", "lamp post", "flickering light"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dumping", "missed collection", "overflowing bin"],
    "Noise": ["noise", "loudspeaker", "loud music", "construction noise", "honking", "sound nuisance"],
    "Road Damage": ["road damaged", "road damage", "cracked road", "broken road", "subsidence", "uneven road"],
    "Heritage Damage": ["heritage", "monument", "vandal", "deface", "historic structure"],
    "Heat Hazard": ["heat", "heatstroke", "extreme heat", "no shade", "no water point", "heat hazard"],
    "Drain Blockage": ["drain blocked", "blocked drain", "clogged drain", "sewage overflow", "drain overflow", "choked drain"],
}


def _to_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _get_complaint_id(row: dict) -> str:
    normalized = {str(key).strip().lower(): value for key, value in (row or {}).items() if key is not None}
    for candidate in ID_FIELD_CANDIDATES:
        value = _to_text(normalized.get(candidate))
        if value:
            return value
    return ""


def _extract_text(row: dict) -> str:
    if not isinstance(row, dict):
        return ""

    lowered = {str(key).strip().lower(): value for key, value in row.items() if key is not None}
    for candidate in TEXT_FIELD_CANDIDATES:
        value = _to_text(lowered.get(candidate))
        if value:
            return value

    fallback_values = []
    for key, value in row.items():
        if key is None:
            continue
        key_text = str(key).strip().lower()
        if key_text in ID_FIELD_CANDIDATES:
            continue
        text_value = _to_text(value)
        if text_value:
            fallback_values.append(text_value)
    return " ".join(fallback_values).strip()


def _contains_keyword(text_lower: str, keywords: list) -> list:
    return [keyword for keyword in keywords if keyword in text_lower]


def _category_matches(text_lower: str) -> dict:
    scores = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        matched_patterns = [pattern for pattern in patterns if pattern in text_lower]
        if matched_patterns:
            scores[category] = matched_patterns
    return scores


def _normalize_reason(reason: str) -> str:
    cleaned = " ".join(_to_text(reason).split())
    if not cleaned:
        cleaned = "Description is missing or insufficient for confident classification"
    if cleaned.endswith("."):
        return cleaned
    return f"{cleaned}."


def _safe_fallback(complaint_id: str, description: str) -> dict:
    text_lower = _to_text(description).lower()
    urgent_matches = _contains_keyword(text_lower, SEVERITY_KEYWORDS)
    priority = "Urgent" if urgent_matches else "Standard"
    if urgent_matches:
        reason = f"The description is insufficient, but it includes '{urgent_matches[0]}' which forces Urgent priority"
    else:
        reason = "The complaint description is missing or insufficient to determine a confident category"
    return {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": priority,
        "reason": _normalize_reason(reason),
        "flag": "NEEDS_REVIEW",
    }

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A taxonomy, priority, reason, and ambiguity rules.
    """
    complaint_id = _get_complaint_id(row)
    description = _extract_text(row)
    text_lower = description.lower()

    if not description:
        return _safe_fallback(complaint_id, description)

    urgent_matches = _contains_keyword(text_lower, SEVERITY_KEYWORDS)
    priority = "Urgent" if urgent_matches else "Standard"
    if not urgent_matches and _contains_keyword(text_lower, LOW_PRIORITY_HINTS):
        priority = "Low"

    matched_categories = _category_matches(text_lower)
    category = "Other"
    flag = ""

    if len(matched_categories) == 1:
        category = next(iter(matched_categories.keys()))
    elif len(matched_categories) > 1:
        top_hits = sorted(matched_categories.items(), key=lambda item: len(item[1]), reverse=True)
        best_category, best_patterns = top_hits[0]
        if len(top_hits) > 1 and len(best_patterns) == len(top_hits[1][1]):
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = best_category
            flag = "NEEDS_REVIEW"
    else:
        flag = "NEEDS_REVIEW"

    reason_parts = []
    if matched_categories and category in matched_categories:
        reason_parts.append(f"Matched '{matched_categories[category][0]}' in the complaint text")
    elif matched_categories and category == "Other":
        conflicting = []
        for _, terms in matched_categories.items():
            conflicting.extend(terms[:1])
        conflicting_phrase = "', '".join(conflicting[:2])
        reason_parts.append(f"Found competing signals like '{conflicting_phrase}'")
    else:
        excerpt = description[:80].strip()
        reason_parts.append(f"The text '{excerpt}' does not clearly match a single allowed category")

    if urgent_matches:
        reason_parts.append(f"includes '{urgent_matches[0]}' which requires Urgent priority")
    elif priority == "Low":
        low_match = _contains_keyword(text_lower, LOW_PRIORITY_HINTS)[0]
        reason_parts.append(f"includes low-severity cue '{low_match}'")
    else:
        reason_parts.append("no mandatory Urgent keyword is present")

    reason = _normalize_reason(" and ".join(reason_parts))

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

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
    
    Reads input CSV, classifies row-wise, and always writes output CSV.
    """
    output_columns = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_out = []

    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig") as in_file:
            reader = csv.DictReader(in_file)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    if not classified.get("reason"):
                        classified["reason"] = _normalize_reason("The complaint description is missing or insufficient to determine a confident category")
                    for col in output_columns:
                        classified.setdefault(col, "")
                    rows_out.append({col: classified.get(col, "") for col in output_columns})
                except Exception:
                    fallback_id = _get_complaint_id(row if isinstance(row, dict) else {})
                    fallback_text = _extract_text(row if isinstance(row, dict) else {})
                    fallback = _safe_fallback(fallback_id, fallback_text)
                    rows_out.append({col: fallback.get(col, "") for col in output_columns})
    except Exception:
        rows_out = rows_out or []

    output_parent = Path(output_path).parent
    output_parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
