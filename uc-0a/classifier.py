"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import re

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

CATEGORY_PATTERNS = [
    ("Pothole", [r"\bpothole\b"]),
    ("Flooding", [r"\bflood(?:ed|s|ing)?\b", r"\bknee-deep\b", r"\bwaterlogging\b"]),
    ("Streetlight", [r"\bstreetlight", r"\blights?\s+out\b", r"\blight(?:s)?\s+flicker"]),
    ("Waste", [r"\bgarbage\b", r"\bwaste\b", r"\bbins?\b", r"\bdead animal\b", r"\bdumped\b"]),
    ("Noise", [r"\bmusic\b", r"\bnoise\b", r"\bmidnight\b"]),
    ("Road Damage", [r"\broad surface\b", r"\bcracked\b", r"\bsinking\b", r"\bfootpath\b", r"\btiles broken\b"]),
    ("Heritage Damage", [r"\bheritage\b"]),
    ("Heat Hazard", [r"\bheat hazard\b", r"\bheatwave\b", r"\bheat stroke\b"]),
    ("Drain Blockage", [r"\bdrain blocked\b", r"\bblocked drain\b", r"\bmanhole\b"]),
]


def _cite_reason(description: str, category: str, priority: str, matched_terms: list) -> str:
    cited = ", ".join(f"'{term}'" for term in matched_terms[:3]) if matched_terms else "the reported wording"
    return (
        f"Classified as {category} with {priority} priority because the description cites {cited}."
    )


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing so category cannot be determined from the complaint text.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    scores = {name: 0 for name in ALLOWED_CATEGORIES if name != "Other"}
    matched = {name: [] for name in scores}

    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            found = re.findall(pattern, text, flags=re.IGNORECASE)
            if found:
                scores[category] += len(found)
                matched[category].extend(found if isinstance(found[0], str) else [pattern])

    positive = [(name, score) for name, score in scores.items() if score > 0]
    flag = ""
    if not positive:
        category = "Other"
        flag = "NEEDS_REVIEW"
        terms = []
    else:
        positive.sort(key=lambda item: item[1], reverse=True)
        top_score = positive[0][1]
        tied = [name for name, score in positive if score == top_score]
        category = tied[0]
        terms = matched[category]
        if len(tied) > 1:
            flag = "NEEDS_REVIEW"

    severity_hits = [word for word in SEVERITY_KEYWORDS if word in text]
    if "children" in text and "child" not in severity_hits:
        severity_hits.append("child")
    priority = "Urgent" if severity_hits else "Standard"
    reason_terms = terms[:2] + severity_hits[:2]
    if not reason_terms:
        reason_terms = [description.split(".")[0][:80]]

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _cite_reason(description, category, priority, reason_terms),
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV. Bad rows are flagged, not dropped."""
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append(
                    {
                        "complaint_id": (row.get("complaint_id") or "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be classified because of error: {exc}.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
