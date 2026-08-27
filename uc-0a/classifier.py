"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple


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

LOW_PRIORITY_KEYWORDS = [
    "minor",
    "small",
    "slight",
    "routine",
    "not urgent",
    "whenever possible",
]

CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole\b", r"\bcrater\b"],
    "Flooding": [r"\bflood(?:ing)?\b", r"\bwaterlogging\b", r"\bwater-?logged\b"],
    "Streetlight": [r"\bstreet\s*light\b", r"\bstreetlight\b", r"\blamp\s*post\b", r"\bdark\s+street\b"],
    "Waste": [r"\bgarbage\b", r"\btrash\b", r"\brubbish\b", r"\bwaste\b", r"\bdump(?:ing|ed)?\b"],
    "Noise": [r"\bnoise\b", r"\bloud\b", r"\bhorn(?:ing)?\b", r"\bconstruction\s+noise\b", r"\bblaring\b"],
    "Road Damage": [r"\broad\s+damage\b", r"\bcrack(?:ed|s)?\b", r"\bbroken\s+road\b", r"\buneven\s+road\b"],
    "Heritage Damage": [r"\bheritage\b", r"\bmonument\b", r"\bhistoric(?:al)?\b", r"\bold\s+structure\b"],
    "Heat Hazard": [r"\bheat\b", r"\bheatwave\b", r"\bhigh\s+temperature\b", r"\bhot\s+surface\b", r"\bheat\s+hazard\b"],
    "Drain Blockage": [r"\bdrain\b", r"\bdrainage\b", r"\bsewer\b", r"\bblocked\b", r"\bclogged\b", r"\bchoked\b"],
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_row_fields(row: dict) -> Tuple[str, str]:
    complaint_id = ""
    description = ""
    for key, value in row.items():
        key_l = (key or "").strip().lower()
        val = "" if value is None else str(value).strip()
        if key_l in {"complaint_id", "id", "ticket_id", "case_id"} and not complaint_id:
            complaint_id = val
        if key_l in {"description", "complaint", "complaint_text", "text", "details", "issue"} and not description:
            description = val
    if not description:
        for value in row.values():
            if value is not None and str(value).strip():
                description = str(value).strip()
                break
    return complaint_id, description


def _find_matches(text: str, patterns: List[str]) -> List[str]:
    matches: List[str] = []
    for pattern in patterns:
        for found in re.findall(pattern, text, flags=re.IGNORECASE):
            token = found if isinstance(found, str) else "".join(found)
            token = token.strip().lower()
            if token and token not in matches:
                matches.append(token)
    return matches


def _infer_priority(text: str) -> Tuple[str, List[str]]:
    urgent_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    if urgent_hits:
        return "Urgent", urgent_hits
    low_hits = [kw for kw in LOW_PRIORITY_KEYWORDS if kw in text]
    if low_hits:
        return "Low", low_hits
    return "Standard", []


def _ensure_one_sentence(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = cleaned.rstrip(".!?;")
    return f"{cleaned}."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A schema in agents.md / skills.md.
    """
    complaint_id, description = _extract_row_fields(row)
    normalized = _normalize_text(description)

    if not normalized:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Category set to Other because no complaint description words were provided for classification.",
            "flag": "NEEDS_REVIEW",
        }

    category_hits: Dict[str, List[str]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        hits = _find_matches(normalized, patterns)
        if hits:
            category_hits[category] = hits

    priority, priority_hits = _infer_priority(normalized)

    if not category_hits:
        reason = _ensure_one_sentence(
            f"Category set to Other because description words \"{description[:80]}\" did not match any allowed category indicators; priority set to {priority}"
        )
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    if len(category_hits) > 1:
        ambiguous_terms = []
        for category, hits in category_hits.items():
            ambiguous_terms.append(f"{category}: {', '.join(hits[:2])}")
        reason = _ensure_one_sentence(
            f"Category set to Other due to ambiguity from words { '; '.join(ambiguous_terms) }; priority set to {priority}"
        )
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    category = next(iter(category_hits))
    supporting_words = ", ".join(category_hits[category][:3])
    if priority == "Urgent" and priority_hits:
        reason = _ensure_one_sentence(
            f"Category set to {category} based on words {supporting_words}, and priority set to Urgent due to severity word {priority_hits[0]}"
        )
    elif priority == "Low" and priority_hits:
        reason = _ensure_one_sentence(
            f"Category set to {category} based on words {supporting_words}, and priority set to Low due to wording {priority_hits[0]}"
        )
    else:
        reason = _ensure_one_sentence(
            f"Category set to {category} based on words {supporting_words}, and priority set to Standard because no severity keyword was found"
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Read input CSV, classify each row, write output CSV.
    Never crashes on bad rows; emits fallback rows with NEEDS_REVIEW.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as in_f, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as out_f:
        reader = csv.DictReader(in_f)
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()

        for row_index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:  # Defensive: preserve batch output on bad rows.
                complaint_id = ""
                if isinstance(row, dict):
                    complaint_id = str(row.get("complaint_id", "") or row.get("id", "")).strip()
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": _ensure_one_sentence(
                        f"Category set to Other because row {row_index} could not be parsed: {str(exc)[:120]}"
                    ),
                    "flag": "NEEDS_REVIEW",
                }

            if result.get("category") not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"
                result["reason"] = _ensure_one_sentence(
                    "Category normalized to Other because classification output was outside allowed labels"
                )

            if result.get("priority") not in {"Urgent", "Standard", "Low"}:
                result["priority"] = "Standard"

            if not str(result.get("reason", "")).strip():
                result["reason"] = "Category set to Other because no valid classification reason could be generated."

            result["reason"] = _ensure_one_sentence(str(result["reason"]))
            if result.get("category") == "Other" and result.get("flag", "") == "":
                result["flag"] = "NEEDS_REVIEW"
            if result.get("category") != "Other":
                result["flag"] = ""

            writer.writerow(
                {
                    "complaint_id": result.get("complaint_id", ""),
                    "category": result.get("category", "Other"),
                    "priority": result.get("priority", "Standard"),
                    "reason": result.get("reason", ""),
                    "flag": result.get("flag", ""),
                }
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
