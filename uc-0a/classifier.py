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

# Deterministic keyword map to keep category labels stable.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "road pit"],
    "Flooding": ["flood", "flooding", "waterlogged", "water logging", "inundated"],
    "Streetlight": ["streetlight", "street light", "lamp post", "dark street", "light not working"],
    "Waste": ["garbage", "trash", "waste", "litter", "dump", "bin overflow", "overflowing bin"],
    "Noise": ["noise", "loud", "horn", "speaker", "construction sound", "dj", "music"],
    "Road Damage": ["road damaged", "broken road", "cracked road", "road crack", "sinkhole", "uneven road"],
    "Heritage Damage": ["heritage", "monument", "historic", "old fort", "temple wall", "vandal"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "hot pavement", "sunstroke", "no shade"],
    "Drain Blockage": ["drain", "drainage", "sewer", "blocked", "clogged", "choked", "manhole overflow"],
}

LOW_PRIORITY_CUES = ["minor", "small", "slight", "occasional", "request", "whenever possible"]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _find_keywords(text: str, keywords: List[str]) -> List[str]:
    found: List[str] = []
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            found.append(kw)
    return found


def _score_categories(text: str) -> List[Tuple[str, List[str]]]:
    scored: List[Tuple[str, List[str]]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = _find_keywords(text, keywords)
        if hits:
            scored.append((category, hits))
    scored.sort(key=lambda item: len(item[1]), reverse=True)
    return scored


def _build_reason(category: str, category_hits: List[str], severity_hits: List[str], ambiguous: bool) -> str:
    if ambiguous:
        if category_hits:
            return (
                "Description contains overlapping words "
                f"{', '.join(category_hits)} so category is marked Other for review."
            )
        if severity_hits:
            return (
                "Description includes urgency words "
                f"{', '.join(severity_hits)} but lacks clear category terms so it is marked Other for review."
            )
        return "Description lacks clear category words, so it is marked Other for review."

    parts: List[str] = []
    if category_hits:
        parts.append(f"Category {category} is supported by words {', '.join(category_hits)}")
    else:
        parts.append(f"Category {category} is assigned from available complaint wording")

    if severity_hits:
        parts.append(f"priority is Urgent because of words {', '.join(severity_hits)}")

    return " and ".join(parts) + "."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A constraints from agents.md and skills.md.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description_raw = str(row.get("description", "") or "")
    description = _normalize_text(description_raw)

    result: Dict[str, str] = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "Description lacks clear category words, so it is marked Other for review.",
        "flag": "NEEDS_REVIEW",
    }

    if not description:
        result["reason"] = "Description is missing, so category is marked Other for review."
        return result

    severity_hits = _find_keywords(description, SEVERITY_KEYWORDS)
    scored = _score_categories(description)

    ambiguous = False
    category_hits: List[str] = []

    if not scored:
        ambiguous = True
        category = "Other"
    else:
        top_category, top_hits = scored[0]
        top_score = len(top_hits)
        tied = [item for item in scored if len(item[1]) == top_score]

        if len(tied) > 1:
            ambiguous = True
            category = "Other"
            combined_hits: List[str] = []
            for _, hits in tied:
                combined_hits.extend(hits)
            # Preserve order while de-duplicating.
            category_hits = list(dict.fromkeys(combined_hits))
        else:
            category = top_category
            category_hits = top_hits

    if severity_hits:
        priority = "Urgent"
    elif _find_keywords(description, LOW_PRIORITY_CUES):
        priority = "Low"
    else:
        priority = "Standard"

    reason = _build_reason(category, category_hits, severity_hits, ambiguous)

    result.update(
        {
            "category": category if category in ALLOWED_CATEGORIES else "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW" if ambiguous else "",
        }
    )
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Reads input CSV, classifies each row, and writes output CSV.
    Must not crash on bad rows; emits fallback rows when classification fails.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
            except Exception as exc:  # pragma: no cover - defensive fallback
                complaint_id = str((row or {}).get("complaint_id", "")).strip() or f"ROW_{idx}"
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing failed with error {type(exc).__name__}, so category is marked Other for review.",
                    "flag": "NEEDS_REVIEW",
                }

            # Ensure exact output shape and legal values.
            sanitized = {
                "complaint_id": str(classified.get("complaint_id", "")).strip(),
                "category": classified.get("category", "Other"),
                "priority": classified.get("priority", "Standard"),
                "reason": str(classified.get("reason", "")).strip() or "Description lacks clear category words, so it is marked Other for review.",
                "flag": classified.get("flag", ""),
            }

            if sanitized["category"] not in ALLOWED_CATEGORIES:
                sanitized["category"] = "Other"
                sanitized["flag"] = "NEEDS_REVIEW"

            if sanitized["priority"] not in {"Urgent", "Standard", "Low"}:
                sanitized["priority"] = "Standard"

            if sanitized["flag"] not in {"", "NEEDS_REVIEW"}:
                sanitized["flag"] = "NEEDS_REVIEW"

            if not sanitized["reason"].endswith("."):
                sanitized["reason"] = sanitized["reason"].rstrip(".") + "."

            writer.writerow(sanitized)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
