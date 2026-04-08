"""
UC-0A — Complaint Classifier
Classifies civic complaints into category, priority, reason, and flag
using keyword-based rules derived from the RICE enforcement spec in agents.md.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword → category mapping. Order matters: first match wins, so more
# specific patterns come before broader ones.
CATEGORY_RULES = [
    ("Heritage Damage",  [r"heritage", r"monument", r"historical", r"archaeological"]),
    ("Heat Hazard",      [r"heat\s*(?:wave|stroke|hazard)", r"sunstroke", r"extreme\s*heat", r"temperature"]),
    ("Drain Blockage",   [r"drain\s*block", r"blocked\s*drain", r"clogged\s*drain", r"manhole", r"sewage", r"sewer"]),
    ("Pothole",          [r"pothole", r"pot\s*hole"]),
    ("Flooding",         [r"flood", r"waterlog", r"water\s*log", r"submerge", r"stranded", r"knee[\s-]*deep", r"waist[\s-]*deep"]),
    ("Streetlight",      [r"streetlight", r"street\s*light", r"lights?\s*out", r"lamp\s*post", r"flickering", r"sparking", r"dark\s*at\s*night"]),
    ("Noise",            [r"noise", r"loud\s*music", r"music\s*past\s*midnight", r"sound\s*pollution", r"honking"]),
    ("Road Damage",      [r"road\s*(surface|damage|crack|sinking|broken|repair)", r"crack", r"sinking",
                          r"footpath.*broken", r"broken.*footpath", r"tiles?\s*broken", r"upturned"]),
    ("Waste",            [r"garbage", r"waste", r"trash", r"rubbish", r"litter", r"dumped",
                          r"dead\s*animal", r"overflowing.*bin", r"bin.*overflow", r"not\s*removed", r"smell"]),
]


def _match_category(description: str) -> tuple:
    """Return (category, matched_keywords) based on description text."""
    desc_lower = description.lower()
    for category, patterns in CATEGORY_RULES:
        matched = [p for p in patterns if re.search(p, desc_lower)]
        if matched:
            return category, matched
    return "Other", []


def _check_severity(description: str) -> list:
    """Return list of severity keywords found in description."""
    desc_lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + kw + r'\b', desc_lower)]


def _build_reason(description: str, category: str, priority: str,
                  matched_patterns: list, severity_hits: list) -> str:
    """Build a reason sentence citing specific words from the description."""
    cited_words = []

    for pattern in matched_patterns[:2]:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            cited_words.append(f'"{match.group()}"')

    for kw in severity_hits[:2]:
        match = re.search(r'\b' + kw + r'\b', description, re.IGNORECASE)
        if match:
            cited_words.append(f'"{match.group()}"')

    if not cited_words:
        cited_words.append(f'"{description[:50].strip()}"')

    word_str = ", ".join(cited_words)
    return f"Classified as {category}/{priority} based on description containing {word_str}."


def _assess_ambiguity(description: str) -> bool:
    """Check if the complaint matches two or more categories with similar confidence."""
    desc_lower = description.lower()
    matching_categories = []
    for category, patterns in CATEGORY_RULES:
        if any(re.search(p, desc_lower) for p in patterns):
            matching_categories.append(category)
    return len(matching_categories) >= 2


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing or unintelligible.",
            "flag": "NEEDS_REVIEW"
        }

    try:
        category, matched_patterns = _match_category(description)
        severity_hits = _check_severity(description)

        if severity_hits:
            priority = "Urgent"
        elif category == "Other":
            priority = "Low"
        else:
            priority = "Standard"

        flag = "NEEDS_REVIEW" if _assess_ambiguity(description) else ""

        reason = _build_reason(description, category, priority,
                               matched_patterns, severity_hits)

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }
    except Exception as e:
        print(f"WARNING: Failed to classify {complaint_id}: {e}", file=sys.stderr)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Classification error — fallback applied.",
            "flag": "NEEDS_REVIEW"
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Resilient: logs warnings for bad rows but never crashes mid-batch.
    """
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            print(f"WARNING: Row {i} failed: {e}", file=sys.stderr)
            results.append({
                "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                "category": "Other",
                "priority": "Low",
                "reason": "Row processing error — fallback applied.",
                "flag": "NEEDS_REVIEW"
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints. Output: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
