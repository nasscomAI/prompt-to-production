"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md (RICE) and skills.md.
"""
import argparse
import csv
import sys

# --- Enforcement constants from agents.md ---

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

# Keyword → category mapping (longest/most-specific match wins)
CATEGORY_KEYWORDS = [
    ("Pothole",         ["pothole", "pot hole", "pothole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlog", "water-log", "inundated", "submerged", "knee-deep"]),
    ("Streetlight",     ["streetlight", "street light", "lamp", "light not working", "light out", "dark road", "no light"]),
    ("Waste",           ["garbage", "waste", "rubbish", "trash", "litter", "dumping", "dump", "refuse", "sanitation"]),
    ("Noise",           ["noise", "loud", "sound", "blaring", "music", "horn", "drilling", "construction sound"]),
    ("Road Damage",     ["road damage", "crack", "broken road", "damaged road", "road broken", "tar", "surface"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "protected structure"]),
    ("Heat Hazard",     ["heat", "hot", "temperature", "heatwave", "heat wave", "burning"]),
    ("Drain Blockage",  ["drain", "drainage", "blocked drain", "sewer", "sewage", "overflow"]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _detect_category(description: str) -> tuple[str, bool]:
    """Return (category, is_ambiguous) by scanning description for keyword matches."""
    lower = description.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in lower for kw in keywords):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    if len(matched) > 1:
        # Multiple matches — return first hit but flag as ambiguous
        return matched[0], True
    return "Other", True


def _detect_priority(description: str) -> str:
    lower = description.lower()
    if any(kw in lower for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """One sentence quoting specific words from description."""
    lower = description.lower()
    cited_words = []

    # Cite severity keyword if present
    for kw in SEVERITY_KEYWORDS:
        if kw in lower:
            cited_words.append(f'"{kw}"')
            break

    # Cite category keyword if present
    for cat, keywords in CATEGORY_KEYWORDS:
        if cat == category:
            for kw in keywords:
                if kw in lower:
                    cited_words.append(f'"{kw}"')
                    break
            break

    if cited_words:
        cited = " and ".join(cited_words)
        return f"Classified as {category} ({priority}) based on {cited} in the description."
    return f"Classified as {category} ({priority}) based on description content."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag.
    Implements all four enforcement rules from agents.md.
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    # Empty / no content — safe fallback (enforcement rule 4)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description provided no classifiable content.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)

    # Enforcement rule 4: ambiguous → Other + NEEDS_REVIEW
    if is_ambiguous and category == "Other":
        flag = "NEEDS_REVIEW"
    elif is_ambiguous:
        # Multiple category signals — keep best match but still flag
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    reason = _build_reason(description, category, priority)

    # Enforce exact allowed values (enforcement rule 1)
    assert category in ALLOWED_CATEGORIES, f"BUG: invalid category '{category}'"

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
    Implements skills.md batch_classify error handling:
    - Aborts with clear message if file/column missing
    - Per-row failures fall back to Other/NEEDS_REVIEW and continue
    """
    # Validate input file
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "description" not in (reader.fieldnames or []):
                print(f"ERROR: '{input_path}' has no 'description' column. "
                      f"Found columns: {reader.fieldnames}", file=sys.stderr)
                sys.exit(1)
            rows = list(reader)
            input_fields = reader.fieldnames or []
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    results = []
    stats = {"total": 0, "urgent": 0, "needs_review": 0}

    for row in rows:
        stats["total"] += 1
        try:
            result = classify_complaint(row)
        except Exception as exc:
            # Per-row failure — degrade gracefully (skills.md error_handling)
            result = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {exc}",
                "flag": "NEEDS_REVIEW",
            }

        if result["priority"] == "Urgent":
            stats["urgent"] += 1
        if result["flag"] == "NEEDS_REVIEW":
            stats["needs_review"] += 1

        # Merge original fields with classification fields
        out_row = {k: row.get(k, "") for k in input_fields}
        out_row.update({
            "category":  result["category"],
            "priority":  result["priority"],
            "reason":    result["reason"],
            "flag":      result["flag"],
        })
        results.append(out_row)

    # Build output field list: original columns + classification columns (no duplicates)
    class_cols = ["category", "priority", "reason", "flag"]
    out_fields = [f for f in input_fields if f not in class_cols] + class_cols

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {stats['total']} complaints — "
          f"{stats['urgent']} Urgent, {stats['needs_review']} flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
