"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

from typing import Dict, List, Tuple

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

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "knee-deep"],
    "Streetlight": ["streetlight", "streetlights", "unlit", "lights out", "flickering", "sparking", "dark at night"],
    "Waste": ["garbage", "waste", "bins", "overflowing", "dumped", "dead animal", "smell"],
    "Noise": ["noise", "music", "midnight", "2am", "loud"],
    "Road Damage": ["cracked", "sinking", "subsidence", "broken", "upturned", "tiles", "road surface", "footpath"],
    "Heritage Damage": ["heritage", "old city", "step well", "ancient"],
    "Heat Hazard": ["heat", "heatwave", "44", "45", "52", "burn", "burns", "melting", "dangerous temperatures", "full sun", "unbearable", "temperature"],
    "Drain Blockage": ["drain blocked", "drainage", "manhole", "blocked drain"],
}

# A small deterministic precedence list avoids random category variation on close scores.
CATEGORY_PRECEDENCE = [
    "Drain Blockage",
    "Flooding",
    "Heat Hazard",
    "Heritage Damage",
    "Road Damage",
    "Streetlight",
    "Waste",
    "Noise",
    "Pothole",
]


def _normalize_text(row: dict) -> str:
    for key in ("description", "complaint", "text", "details"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _find_keyword_hits(text_lower: str, keywords: List[str]) -> List[str]:
    hits: List[str] = []
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", text_lower):
            hits.append(kw)
    return hits


def _extract_exact_snippet(description: str, term: str) -> str:
    match = re.search(rf"\b{re.escape(term)}\b", description, flags=re.IGNORECASE)
    if not match:
        return term
    return description[match.start():match.end()]


def _category_signal(text_lower: str) -> Dict[str, List[str]]:
    signals: Dict[str, List[str]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = _find_keyword_hits(text_lower, keywords)
        if hits:
            signals[category] = hits
    return signals


def _classify_with_ambiguity(signals: Dict[str, List[str]]) -> Tuple[str, bool, List[str]]:
    if not signals:
        return "Other", True, []

    ranked = sorted(
        signals.items(),
        key=lambda item: (-len(item[1]), CATEGORY_PRECEDENCE.index(item[0]) if item[0] in CATEGORY_PRECEDENCE else 999),
    )
    top_category, top_hits = ranked[0]
    top_score = len(top_hits)

    if len(ranked) > 1:
        second_category, second_hits = ranked[1]
        second_score = len(second_hits)

        # Genuine ambiguity: tied top scores.
        if second_score == top_score:
            evidence = sorted(set(top_hits + second_hits))
            return "Other", True, evidence

        # Genuine ambiguity: highly overlapping categories with close evidence.
        overlap_ambiguity = (
            {top_category, second_category} in [
                {"Flooding", "Drain Blockage"},
                {"Heat Hazard", "Road Damage"},
                {"Streetlight", "Heritage Damage"},
            ]
            and (top_score - second_score) <= 1
        )
        if overlap_ambiguity:
            evidence = sorted(set(top_hits + second_hits))
            return "Other", True, evidence

    return top_category, False, sorted(set(top_hits))


def _build_reason(category: str, priority: str, exact_terms: List[str], fallback_description: str) -> str:
    if exact_terms:
        terms = ", ".join(f"'{term}'" for term in exact_terms[:3])
        return f"Classified as {category} with {priority} priority based on words {terms} in the complaint description."

    if fallback_description:
        first_word = fallback_description.split()[0]
        return f"Classified as {category} with {priority} priority based on word '{first_word}' in the complaint description."

    return f"Classified as {category} with {priority} priority based on words 'no description' in the complaint description."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A rules from agents.md and skills.md.
    """
    complaint_id = row.get("complaint_id", "")
    description = _normalize_text(row)
    text_lower = description.lower()

    # Extended urgent triggers requested for UC-0A.
    urgent_terms = SEVERITY_KEYWORDS + [
        "flooded",
        "knee-deep",
        "standing in water",
        "stranded",
        "inaccessible",
        "risk",
    ]
    severity_hits = _find_keyword_hits(text_lower, urgent_terms)
    priority = "Urgent" if severity_hits else ("Standard" if description else "Low")

    # Deterministic category mapping with explicit priority over "Other".
    category_rules = {
        "Pothole": ["pothole", "potholes"],
        "Flooding": ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "standing in water", "stranded", "inaccessible"],
        "Streetlight": ["streetlight", "streetlights", "lights out", "dark", "unlit", "flickering", "sparking"],
        "Waste": ["garbage", "waste", "bins", "overflowing", "dumped", "dead animal", "smell"],
        "Noise": ["noise", "music", "midnight", "2am", "loud"],
        "Road Damage": ["cracked", "sinking", "subsidence", "broken", "upturned", "tiles", "road surface", "footpath"],
        "Heritage Damage": ["heritage", "old city", "step well", "ancient"],
        "Heat Hazard": ["heat", "heatwave", "melting", "dangerous temperatures", "full sun", "unbearable", "temperature", "burn", "burns"],
        "Drain Blockage": ["manhole", "drain", "drain blocked", "blocked drain", "blocked"],
    }
    precedence = [
        "Drain Blockage",
        "Flooding",
        "Streetlight",
        "Heat Hazard",
        "Road Damage",
        "Waste",
        "Noise",
        "Heritage Damage",
        "Pothole",
    ]

    category_hits: Dict[str, List[str]] = {}
    for category, terms in category_rules.items():
        hits = _find_keyword_hits(text_lower, terms)
        if hits:
            category_hits[category] = hits

    if category_hits:
        ranked = sorted(
            category_hits.items(),
            key=lambda item: (-len(item[1]), precedence.index(item[0]) if item[0] in precedence else 999),
        )
        predicted_category = ranked[0][0]
        category_terms = ranked[0][1]
        flag = ""
    else:
        predicted_category = "Other"
        category_terms = []
        flag = "NEEDS_REVIEW"

    if predicted_category not in ALLOWED_CATEGORIES:
        predicted_category = "Other"
        flag = "NEEDS_REVIEW"

    evidence_terms = severity_hits + category_terms
    exact_terms = [_extract_exact_snippet(description, term) for term in evidence_terms]
    exact_terms = list(dict.fromkeys([term for term in exact_terms if term]))

    if exact_terms:
        quoted = ", ".join(f"'{term}'" for term in exact_terms[:4])
        if priority == "Urgent" and severity_hits:
            reason = f"Matched {quoted}; severity terms indicate immediate risk, so priority is Urgent and category is {predicted_category}."
        else:
            reason = f"Matched {quoted}; these words map this complaint to category {predicted_category} with priority {priority}."
    elif description:
        first_word = description.split()[0]
        reason = f"Only word '{first_word}' was usable, so category is {predicted_category} with priority {priority}."
    else:
        reason = "No description text was available, so category is Other with priority Low and manual review is required."

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": predicted_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Reads input CSV, classifies each row, and writes output CSV.
    Must not crash on bad rows and must preserve all input rows.
    """
    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row")

        output_fieldnames = list(reader.fieldnames)
        for new_col in ("category", "priority", "reason", "flag"):
            if new_col not in output_fieldnames:
                output_fieldnames.append(new_col)

        output_rows = []
        for row in reader:
            safe_row = dict(row) if row is not None else {}
            try:
                result = classify_complaint(safe_row)
            except Exception as exc:
                result = {
                    "complaint_id": safe_row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classified as Other with review required due to row processing error: {type(exc).__name__}.",
                    "flag": "NEEDS_REVIEW",
                }

            merged = dict(safe_row)
            merged["category"] = result["category"]
            merged["priority"] = result["priority"]
            merged["reason"] = result["reason"]
            merged["flag"] = result["flag"]
            output_rows.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
