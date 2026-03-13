"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path


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

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_RULES = [
    (
        "Drain Blockage",
        ("drain blocked", "blocked drain", "clogged drain", "drain choke", "drainage blocked"),
    ),
    (
        "Flooding",
        (
            "flood",
            "flooded",
            "waterlogged",
            "water logging",
            "underpass flooded",
            "standing in water",
            "knee-deep",
        ),
    ),
    (
        "Streetlight",
        ("streetlight", "streetlights", "lights out", "flickering", "sparking", "dark at night"),
    ),
    (
        "Waste",
        (
            "garbage",
            "waste",
            "bins",
            "dumped",
            "dumping",
            "dead animal",
            "smell",
            "overflowing",
        ),
    ),
    (
        "Noise",
        ("music past midnight", "noise", "loudspeaker", "wedding venue", "past midnight"),
    ),
    (
        "Heritage Damage",
        ("heritage",),
    ),
    (
        "Pothole",
        ("pothole", "potholes"),
    ),
    (
        "Road Damage",
        (
            "road surface cracked",
            "sinking",
            "footpath",
            "tiles broken",
            "manhole cover missing",
            "road damage",
            "cracked",
        ),
    ),
    (
        "Heat Hazard",
        ("heat", "heatstroke", "hot pavement", "no shade"),
    ),
]


def _normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _matching_keywords(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if keyword in text]


def _detect_category(description: str) -> tuple[str, list[str], bool]:
    matches: list[tuple[str, list[str]]] = []
    for category, keywords in CATEGORY_RULES:
        matched = _matching_keywords(description, keywords)
        if matched:
            matches.append((category, matched))

    if not matches:
        return "Other", [], True

    if len(matches) == 1:
        return matches[0][0], matches[0][1], False

    prioritized_categories = [category for category, _ in matches]
    if "Drain Blockage" in prioritized_categories and "Flooding" in prioritized_categories:
        drain_keywords = next(words for category, words in matches if category == "Drain Blockage")
        return "Drain Blockage", drain_keywords, False

    chosen_category, chosen_keywords = matches[0]
    return chosen_category, chosen_keywords, True


def _detect_priority(category: str, description: str, days_open: str) -> tuple[str, list[str]]:
    severity_hits = sorted(keyword for keyword in SEVERITY_KEYWORDS if keyword in description)
    if severity_hits:
        return "Urgent", severity_hits

    try:
        open_days = int((days_open or "").strip())
    except ValueError:
        open_days = 0

    if open_days >= 14:
        return "Standard", [f"days_open={open_days}"]
    if category in {"Noise", "Waste"} and open_days <= 7:
        return "Low", [f"days_open={open_days}"] if open_days else []
    return "Standard", [f"days_open={open_days}"] if open_days >= 7 else []


def _build_reason(category: str, category_hits: list[str], priority: str, priority_hits: list[str], ambiguous: bool) -> str:
    evidence = category_hits or [category.lower()]
    evidence_text = ", ".join(f"'{item}'" for item in evidence[:3])
    if priority_hits:
        priority_text = ", ".join(f"'{item}'" for item in priority_hits[:3])
        sentence = f"Classified as {category} based on {evidence_text}; priority is {priority} because of {priority_text}."
    else:
        sentence = f"Classified as {category} based on {evidence_text}; no urgent severity keywords were found so priority is {priority}."

    if ambiguous:
        return sentence[:-1] + " and the row should be reviewed for overlap."
    return sentence

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row or {}).get("complaint_id", "")
    description = _normalize((row or {}).get("description", ""))
    days_open = (row or {}).get("days_open", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing, so the complaint cannot be classified from the row alone.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_hits, ambiguous = _detect_category(description)
    priority, priority_hits = _detect_priority(category, description, days_open)
    reason = _build_reason(category, category_hits, priority, priority_hits, ambiguous)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if ambiguous or category == "Other" else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8", newline="") as source, output_file.open(
        "w", encoding="utf-8", newline=""
    ) as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=output_fields)
        writer.writeheader()

        for raw_row in reader:
            try:
                result = classify_complaint(raw_row)
            except Exception as exc:  # pragma: no cover - defensive batch guarantee
                result = {
                    "complaint_id": raw_row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row could not be processed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            if result["category"] not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"
                result["reason"] = "Classifier produced an invalid category and the row requires review."

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
