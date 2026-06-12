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

CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "stranded"],
    "Streetlight": ["streetlight", "streetlights", "lights out", "dark at night", "flickering", "sparking"],
    "Waste": ["garbage", "waste", "overflowing bins", "dead animal", "smell", "dumped"],
    "Noise": ["noise", "loud", "music past midnight", "weeknights", "wedding venue"],
    "Road Damage": ["road surface cracked", "sinking", "broken", "upturned", "tiles broken", "utility work"],
    "Heritage Damage": ["heritage", "old city", "monument", "historic"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "hot pavement", "dehydration"],
    "Drain Blockage": ["drain blocked", "drain blockage", "manhole", "clogged drain", "drain choke"],
}


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _find_matches(text: str, patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for pattern in patterns:
        if pattern in text:
            hits.append(pattern)
    return hits


def _pick_category(description_lc: str) -> tuple[str, list[str], bool]:
    """
    Returns (category, matched_terms, ambiguous).
    """
    category_hits: dict[str, list[str]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        hits = _find_matches(description_lc, patterns)
        if hits:
            category_hits[category] = hits

    if not category_hits:
        return "Other", [], True

    # Use the category with the highest number of pattern hits.
    ranked = sorted(category_hits.items(), key=lambda item: len(item[1]), reverse=True)
    best_category, best_hits = ranked[0]
    best_score = len(best_hits)
    tied = [c for c, h in ranked if len(h) == best_score]

    if len(tied) > 1:
        return "Other", [], True

    return best_category, best_hits, False


def _pick_priority(description_lc: str, category: str) -> tuple[str, list[str]]:
    severity_hits = _find_matches(description_lc, SEVERITY_KEYWORDS)
    if severity_hits:
        return "Urgent", severity_hits

    # Conservative Low assignment for minor nuisance wording.
    low_words = ["flickering", "smell", "weeknights", "past midnight"]
    low_hits = _find_matches(description_lc, low_words)
    if low_hits and category in {"Noise", "Waste", "Streetlight"}:
        return "Low", low_hits

    return "Standard", []


def _build_reason(category: str, category_hits: list[str], priority_hits: list[str], ambiguous: bool) -> str:
    if ambiguous:
        return "Category is ambiguous from the complaint text, so it is marked for review."

    if priority_hits:
        return (
            f"Classified as {category} because description includes '{category_hits[0] if category_hits else category.lower()}' "
            f"and urgency indicator '{priority_hits[0]}'."
        )

    if category_hits:
        return f"Classified as {category} because description includes '{category_hits[0]}'."

    return f"Classified as {category} based on complaint wording."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Deterministic, keyword-based mapping aligned to UC-0A agents.md enforcement.
    """
    complaint_id = (row or {}).get("complaint_id", "")
    description = (row or {}).get("description", "")
    description_lc = _normalize(description)

    if not description_lc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so category cannot be determined from text.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_hits, ambiguous = _pick_category(description_lc)
    priority, priority_hits = _pick_priority(description_lc, category)
    flag = "NEEDS_REVIEW" if ambiguous else ""
    reason = _build_reason(category, category_hits, priority_hits, ambiguous)

    # Guardrails for strict schema compliance.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in {"Urgent", "Standard", "Low"}:
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
    
    Reads input CSV, classifies each row, and writes schema-compliant output.
    Continues on bad rows and emits a safe fallback result instead of crashing.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8", newline="") as infile, open(
        output_path, "w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                # Keep batch output stable even if a single row is malformed.
                result = {
                    "complaint_id": (row or {}).get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be processed reliably and is flagged for manual review.",
                    "flag": "NEEDS_REVIEW",
                }

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
