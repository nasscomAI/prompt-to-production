"""
UC-0A — Complaint Classifier
Built with the RICE workflow; enforcement rules in agents.md.
Runs on data/city-test-files/test_pune.csv and writes uc-0a/results_pune.csv.
"""
import argparse
import csv
import re

CATEGORIES = [
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
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

# Category -> list of phrases that trigger it. Matching is case-insensitive substring.
CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "waterlog", "water logging", "knee-deep"]),
    ("Streetlight", ["streetlight", "lights out", "light", "lamp"]),
    ("Waste", ["garbage", "waste", "dead animal", "litter", "bin", "debris", "dumped"]),
    ("Noise", ["noise", "music", "loud"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "footpath", "pavement", "manhole", "upturned"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat"]),
    ("Drain Blockage", ["drain", "drainage"]),
]


def _text(row: dict) -> str:
    return str(row.get("description", "")).strip().lower()


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = _text(row)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description unavailable",
            "flag": "NEEDS_REVIEW",
        }

    # Severity check — must trigger Urgent.
    hits = [k for k in SEVERITY_KEYWORDS if k in description]
    priority = "Urgent" if hits else "Standard"

    # Category matching: every rule that matches at least one phrase scores.
    scored = []
    for category, phrases in CATEGORY_RULES:
        matched = [p for p in phrases if p in description]
        if matched:
            scored.append((category, matched))

    if not scored:
        category = "Other"
        matched = []
        flag = ""
    elif len(scored) == 1:
        category, matched = scored[0]
        flag = ""
    else:
        # Multiple distinct categories match -> genuinely ambiguous.
        scored.sort(key=lambda x: (-len(x[1]), CATEGORIES.index(x[0])))
        category, matched = scored[0]
        flag = "NEEDS_REVIEW"

    # One-sentence reason quoting exact words from the description.
    quoted = ", ".join(f"'{w}'" for w in matched)
    if category == "Other":
        reason = "No category keyword found in description"
    elif flag == "NEEDS_REVIEW":
        reason = f"Ambiguous: matched '{category}' via {quoted} but other categories also fit"
    else:
        reason = f"Matched '{category}' via {quoted}"

    if priority == "Urgent":
        reason += f"; Urgent because description contains '{hits[0]}'"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            rows.append(raw)

    results = []
    flagged = 0
    urgent = 0
    for raw in rows:
        try:
            out = classify_complaint(raw)
        except Exception:
            out = {
                "complaint_id": raw.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "Row could not be classified",
                "flag": "NEEDS_REVIEW",
            }
        results.append(out)
        if out["flag"] == "NEEDS_REVIEW":
            flagged += 1
        if out["priority"] == "Urgent":
            urgent += 1

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows -> {output_path}")
    print(f"  Urgent rows: {urgent}")
    print(f"  NEEDS_REVIEW rows: {flagged}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
