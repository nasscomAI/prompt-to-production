"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md (RICE) and skills.md.
"""
import argparse
import csv
import os

# --- RICE: enforcement constants ---

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (order matters: more specific first)
CATEGORY_KEYWORDS = [
    ("Pothole",         ["pothole", "potholes", "potholed"]),
    ("Flooding",        ["flood", "flooding", "flooded", "waterlogging", "waterlogged"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "lamppost", "light out", "lights out", "no light"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter", "dumping", "dump", "stench", "smell"]),
    ("Noise",           ["noise", "noisy", "loud", "sound", "music", "horn", "honking"]),
    ("Road Damage",     ["road damage", "broken road", "cracked road", "road crack", "road broken", "damaged road"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "statue", "temple wall", "fort"]),
    ("Heat Hazard",     ["heat", "hot", "temperature", "sun", "fire hazard", "overheating"]),
    ("Drain Blockage",  ["drain", "drainage", "sewer", "blocked drain", "clogged", "overflow", "manhole"]),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Return (category, is_ambiguous).
    Matches against CATEGORY_KEYWORDS; returns ('Other', True) if nothing matches.
    """
    text = description.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    if len(matched) > 1:
        # Multiple matches — return first (most specific), flag as ambiguous
        return matched[0], True
    return "Other", True


def _detect_priority(description: str) -> str:
    """Return 'Urgent' if any severity keyword is present, else 'Standard'."""
    text = description.lower()
    if any(kw in text for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """One sentence citing specific words from the description."""
    text = description.lower()

    # Find the triggering severity keyword if Urgent
    triggered_by = next((kw for kw in SEVERITY_KEYWORDS if kw in text), None)

    # Find the matching category keyword
    category_trigger = None
    for cat, keywords in CATEGORY_KEYWORDS:
        if cat == category:
            category_trigger = next((kw for kw in keywords if kw in text), None)
            break

    parts = []
    if category_trigger:
        parts.append(f"classified as '{category}' due to '{category_trigger}'")
    else:
        parts.append(f"classified as '{category}'")

    if triggered_by:
        parts.append(f"marked Urgent due to '{triggered_by}'")

    return "Complaint " + "; ".join(parts) + "."


def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description.
    Returns dict with: category, priority, reason, flag.
    Enforces all RICE rules from agents.md.
    """
    # Handle empty input
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description was empty — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    # RICE enforcement: category must be in the allowed taxonomy
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row using classify_complaint, write results CSV.
    Appends category, priority, reason, flag columns to all original columns.
    Prints summary on completion. Never silently skips or halts mid-batch.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "description" not in reader.fieldnames:
            found = reader.fieldnames or []
            raise ValueError(
                f"'description' column not found in input CSV. "
                f"Columns present: {found}"
            )
        rows = list(reader)
        original_fields = list(reader.fieldnames)

    output_fields = original_fields + ["category", "priority", "reason", "flag"]
    results = []
    total = urgent_count = needs_review_count = 0

    for row in rows:
        total += 1
        description = row.get("description", "")
        try:
            classification = classify_complaint(description)
        except Exception as exc:
            classification = {
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error — {exc}",
                "flag": "NEEDS_REVIEW",
            }

        row.update(classification)
        results.append(row)

        if classification["priority"] == "Urgent":
            urgent_count += 1
        if classification["flag"] == "NEEDS_REVIEW":
            needs_review_count += 1

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed : {total} rows")
    print(f"Urgent    : {urgent_count}")
    print(f"NEEDS_REVIEW: {needs_review_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
