"""
UC-0A - Complaint Classifier
Deterministic, rule-based classifier aligned to README constraints.
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
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

# Category signals are intentionally explicit to avoid taxonomy drift.
CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpothole(s)?\b",
    ],
    "Flooding": [
        r"\bflood(ed|ing|s)?\b",
        r"\bwaterlogging\b",
        r"\bunderpass flooded\b",
        r"\bknee[- ]deep\b",
        r"\binaccessible\b.*\brain\b",
    ],
    "Streetlight": [
        r"\bstreet ?light(s)?\b",
        r"\blights? out\b",
        r"\bflicker(ing)?\b",
        r"\bsparking\b",
        r"\bdark at night\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\bbin(s)?\b",
        r"\bbulk waste\b",
        r"\bdead animal\b",
        r"\boverflowing\b.*\bbin(s)?\b",
        r"\bdumped\b",
    ],
    "Noise": [
        r"\bnoise\b",
        r"\bloud\b",
        r"\bmusic\b",
        r"\bpast midnight\b",
        r"\bweeknight(s)?\b",
    ],
    "Road Damage": [
        r"\broad surface\b",
        r"\bcrack(ed|s|ing)?\b",
        r"\bsink(ing)?\b",
        r"\bbroken\b.*\b(footpath|tiles?)\b",
        r"\bupturned\b",
        r"\bmanhole cover missing\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b.*\b(damage|crack(ed|s|ing)?|collapse|deface(d|ment)?)\b",
        r"\bold city\b",
        r"\bmonument\b",
        r"\bhistoric\b",
    ],
    "Heat Hazard": [
        r"\bheat\b",
        r"\bheatwave\b",
        r"\bhigh temperature\b",
        r"\bsunstroke\b",
        r"\bdehydration\b",
    ],
    "Drain Blockage": [
        r"\bdrain(s)?\b.*\bblock(ed|age)?\b",
        r"\bblocked drain(s)?\b",
        r"\bclogged drain(s)?\b",
        r"\bmanhole\b.*\bblock(ed|age)?\b",
    ],
}

# Used as tie-breaker when two categories score the same.
CATEGORY_PRECEDENCE = [
    "Drain Blockage",
    "Flooding",
    "Pothole",
    "Streetlight",
    "Road Damage",
    "Waste",
    "Noise",
    "Heritage Damage",
    "Heat Hazard",
]


def _normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def _find_description_field(row: Dict[str, str]) -> str:
    preferred = ["description", "complaint_description", "complaint_text", "text"]
    for field in preferred:
        if field in row:
            return row.get(field, "")
    return ""


def _extract_category_signals(text: str) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    scores: Dict[str, int] = {c: 0 for c in CATEGORY_PATTERNS}
    evidence: Dict[str, List[str]] = {c: [] for c in CATEGORY_PATTERNS}
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                scores[category] += 1
                evidence[category].append(match.group(0))
    return scores, evidence


def _choose_category(scores: Dict[str, int]) -> Tuple[str, bool]:
    max_score = max(scores.values()) if scores else 0
    if max_score <= 0:
        return "Other", True

    top = [category for category, score in scores.items() if score == max_score]
    if len(top) == 1:
        return top[0], False

    for candidate in CATEGORY_PRECEDENCE:
        if candidate in top:
            return candidate, True
    return top[0], True


def _contains_severity_keyword(text: str) -> Tuple[bool, List[str]]:
    found = []
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text, flags=re.IGNORECASE):
            found.append(keyword)
    return len(found) > 0, found


def _build_reason(category: str, evidence: List[str], severity_hits: List[str], text: str) -> str:
    quoted = []
    for token in evidence:
        token_clean = token.strip()
        if token_clean and token_clean.lower() not in [t.lower() for t in quoted]:
            quoted.append(token_clean)
    for token in severity_hits:
        if token.lower() not in [t.lower() for t in quoted]:
            quoted.append(token)

    if not quoted:
        # Fall back to a short text slice so reason always cites source words.
        snippet = " ".join(text.split()[:8]).strip()
        if snippet:
            quoted = [snippet]
        else:
            quoted = ["no usable description text"]

    joined = ", ".join([f"'{q}'" for q in quoted[:3]])
    return f"Classified as {category} based on words {joined} in the complaint description."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = _find_description_field(row)
    normalized = _normalize_text(description)

    if not normalized:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    scores, evidence_map = _extract_category_signals(normalized)
    category, ambiguous = _choose_category(scores)

    has_severity, severity_hits = _contains_severity_keyword(normalized)
    if has_severity:
        priority = "Urgent"
    elif category in ("Flooding", "Drain Blockage", "Road Damage", "Pothole", "Streetlight"):
        priority = "Standard"
    else:
        priority = "Low"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        ambiguous = True

    reason = _build_reason(
        category=category,
        evidence=evidence_map.get(category, []),
        severity_hits=severity_hits,
        text=description,
    )

    flag = "NEEDS_REVIEW" if ambiguous else ""
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    output_rows = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no header row.")

            has_description = any(
                name in reader.fieldnames
                for name in ["description", "complaint_description", "complaint_text", "text"]
            )
            if not has_description:
                raise ValueError(
                    "Input CSV is missing a description column. Expected one of: "
                    "description, complaint_description, complaint_text, text."
                )

            for idx, row in enumerate(reader, start=1):
                try:
                    classified = classify_complaint(row)
                    if not classified.get("complaint_id"):
                        classified["complaint_id"] = f"ROW-{idx}"
                        if not classified.get("flag"):
                            classified["flag"] = "NEEDS_REVIEW"
                            classified["reason"] = (
                                "Classified with fallback because complaint_id is missing."
                            )
                    output_rows.append(classified)
                except Exception as row_error:
                    output_rows.append(
                        {
                            "complaint_id": (row.get("complaint_id") or f"ROW-{idx}").strip(),
                            "category": "Other",
                            "priority": "Low",
                            "reason": f"Row failed classification: {str(row_error)}.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
    except FileNotFoundError as file_error:
        raise FileNotFoundError(f"Input file not found: {input_path}") from file_error

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["complaint_id", "category", "priority", "reason", "flag"],
        )
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
