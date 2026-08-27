"""
UC-0A — Complaint Classifier
Built with the RICE → agents.md → skills.md → CRAFT workflow.
Enforcement rules mirror uc-0a/agents.md.
"""
import argparse
import csv
import re

# Locked schema — exact strings only (agents.md enforcement rule 1).
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Keyword rules per category. Matching is case-insensitive substring on the
# description. A category may only be assigned from this table — never invented.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "knee-deep", "waterlogg", "standing in water", "rainwater"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "unlit"],
    "Waste": ["garbage", "waste", "dump", "bin", "litter"],
    "Noise": ["music", "noise", "loudspeaker", "drilling", "idling", "band playing"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles broken",
                    "pavement", "paving", "road collapsed", "crater"],
    "Heritage Damage": ["heritage", "historic", "cobblestone"],
    "Heat Hazard": ["heat", "sunstroke", "melting", "temperature", "°c", "full sun"],
    "Drain Blockage": ["drain", "manhole", "sewer"],
}

# Weak keywords: suggestive but not conclusive — a weak-only match must be
# treated as ambiguous (agents.md refusal condition).
WEAK_KEYWORDS = {
    "Waste": ["dead animal", "smell"],
    "Streetlight": ["darkness"],
}

# Severity keywords that must force priority Urgent (agents.md enforcement
# rule 2). Patterns cover inflections (child → children, injury → injured).
SEVERITY_PATTERNS = {
    "injury": r"injur\w*",
    "child": r"child\w*",
    "school": r"school\w*",
    "hospital": r"hospital\w*",
    "ambulance": r"ambulance\w*",
    "fire": r"fire\w*",
    "hazard": r"hazard\w*",
    "fell": r"fell",
    "collapse": r"collaps\w*",
}


def find_severity_words(description: str):
    """Return the actual severity words found in the description."""
    hits = []
    for pattern in SEVERITY_PATTERNS.values():
        found = re.findall(rf"\b{pattern}\b", description, flags=re.IGNORECASE)
        hits.extend(found)
    return hits


def actual_words(description: str, keywords):
    """Expand matched keyword substrings to the words as written in the description."""
    lower = description.lower()
    words = []
    for kw in keywords:
        idx = lower.find(kw)
        if idx == -1:
            continue
        start, end = idx, idx + len(kw)
        while start > 0 and (lower[start - 1].isalnum() or lower[start - 1] == "°"):
            start -= 1
        while end < len(lower) and (lower[end].isalnum() or lower[end] == "°"):
            end += 1
        words.append(description[start:end])
    return words or list(keywords)


def quote(words):
    return ", ".join(f'"{w}"' for w in words)


def match_categories(description_lower: str):
    """Return {category: [matched keywords]} for strong and weak tables."""
    strong, weak = {}, {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in description_lower]
        if hits:
            strong[category] = hits
    for category, keywords in WEAK_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in description_lower]
        if hits:
            weak[category] = hits
    return strong, weak


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "UNKNOWN").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty, so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    strong, weak = match_categories(description.lower())

    flag = ""
    ambiguity_note = ""
    if strong:
        # Highest keyword count wins; ties resolved by schema order.
        best = max(
            strong,
            key=lambda c: (len(strong[c]), -ALLOWED_CATEGORIES.index(c)),
        )
        cited = actual_words(description, strong[best])
        tied = [c for c in strong if c != best and len(strong[c]) == len(strong[best])]
        if tied:
            flag = "NEEDS_REVIEW"
            tied_words = [w for c in tied for w in actual_words(description, strong[c])]
            ambiguity_note = (
                f", flagged because {quote(tied_words)} equally suggests "
                f"{' / '.join(tied)}"
            )
        category_note = f"matched {quote(cited)}"
    elif weak:
        best = next(iter(weak))
        cited = actual_words(description, weak[best])
        flag = "NEEDS_REVIEW"
        ambiguity_note = f", flagged because {quote(cited)} is only a weak indicator"
        category_note = f"weakly matched {quote(cited)}"
    else:
        best = "Other"
        flag = "NEEDS_REVIEW"
        ambiguity_note = ", flagged because no category keyword matched"
        category_note = "no category keywords found in the description"

    severity_hits = find_severity_words(description)
    if severity_hits:
        priority = "Urgent"
        priority_note = f"severity keyword {quote(severity_hits)} forces Urgent"
    elif best == "Noise":
        priority = "Low"
        priority_note = "non-safety nuisance with no severity keywords"
    else:
        priority = "Standard"
        priority_note = "no severity keywords present"

    return {
        "complaint_id": complaint_id,
        "category": best,
        "priority": priority,
        "reason": f"Category {best}: {category_note}; priority {priority}: "
                  f"{priority_note}{ambiguity_note}.",
        "flag": flag,
    }


OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:  # a bad row must never kill the batch
                results.append({
                    "complaint_id": (row.get("complaint_id") or "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be classified ({exc}).",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
