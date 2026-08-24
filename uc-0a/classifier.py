"""
UC-0A — Complaint Classifier
Deterministic, rules-based classification of citizen complaints into the fixed
UC-0A taxonomy. Implements the contracts defined in agents.md and skills.md:
exact category strings, keyword-driven Urgent priority, quoted justification,
and NEEDS_REVIEW surfacing of genuine ambiguity.
"""
import argparse
import csv
import re
import sys

CATEGORIES = (
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
)

OUTPUT_COLUMNS = ("complaint_id", "category", "priority", "reason", "flag")

SEVERITY_PATTERNS = (
    ("injury",    re.compile(r"\binjur\w*", re.I)),
    ("child",     re.compile(r"\bchild\w*", re.I)),
    ("school",    re.compile(r"\bschool\w*", re.I)),
    ("hospital",  re.compile(r"\bhospital\w*", re.I)),
    ("ambulance", re.compile(r"\bambulances?\b", re.I)),
    ("fire",      re.compile(r"\bfires?\b", re.I)),
    ("hazard",    re.compile(r"\bhazard\w*", re.I)),
    ("fell",      re.compile(r"\bfell\b|\bfalls?\b|\bfalling\b|\bfallen\b", re.I)),
    ("collapse",  re.compile(r"\bcollaps\w*", re.I)),
)


def _rules(*patterns):
    return [re.compile(p, re.I) for p in patterns]


CATEGORY_RULES = {
    "Pothole": _rules(
        r"\bpotholes?\b", r"\bpot\s?holes?\b",
    ),
    "Flooding": _rules(
        r"\bflood\w*", r"water\s?log\w*", r"\bsubmerg\w*|\binundat\w*",
        r"\bstanding water\b",
    ),
    "Streetlight": _rules(
        r"\bstreet\s?lights?\b", r"\blamp\s?posts?\b", r"\blights?\s+out\b",
        r"\bunlit\b", r"\bdark(?:ness)?\b",
    ),
    "Waste": _rules(
        r"\bwastes?\b", r"\bgarbage\b", r"\btrash\b", r"\blitter\w*",
        r"\bdump\w*", r"\bdead animals?\b", r"\bbins?\b",
    ),
    "Noise": _rules(
        r"\bmusic\b", r"\bnois[ey]\w*", r"\bamplifier\w*", r"\bloudspeakers?\b",
        r"\bdrill\w*", r"\bbands?\b",
    ),
    "Road Damage": _rules(
        r"\bsub\s?sid\w*", r"\bbuckl\w*", r"\bcrack\w*", r"\bsink\w*|\bsunken\b",
        r"\bcraters?\b", r"\bcollaps\w*", r"\bfootpaths?\b", r"\bpav\w*",
        r"\btiles?\b", r"\bcobblestones?\b", r"\bupturn\w*", r"\broad surface\b",
    ),
    "Heritage Damage": _rules(
        r"\bheritage\b", r"\bhistoric\w*", r"\bancient\b", r"\bmonuments?\b",
        r"\bdefac\w*", r"\bstep wells?\b",
    ),
    "Heat Hazard": _rules(
        r"\bheat\w*", r"°\s?C", r"\btemperatures?\b", r"\bmelt\w*",
        r"\bbubbl\w*", r"\bunbearabl\w*", r"exposed to (the )?(full )?sun",
        r"\bscorch\w*",
    ),
    "Drain Blockage": _rules(
        r"\bblock(?:ed|age|ing)?\b", r"\bclogg?\w*",
        r"\bstormwater drains?\b", r"\bmain drains?\b",
    ),
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    severity_hits = [
        mo.group(0) for _, rx in SEVERITY_PATTERNS if (mo := rx.search(description))
    ]
    priority = "Urgent" if severity_hits else "Standard"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "No description text available to justify any category.",
            "flag": "NEEDS_REVIEW",
        }

    scored = []
    for category in CATEGORIES:
        if category == "Other":
            continue
        hits = list(dict.fromkeys(
            m.group(0)
            for rx in CATEGORY_RULES[category]
            if (m := rx.search(description))
        ))
        scored.append((len(hits), CATEGORIES.index(category), category, hits))
    scored.sort(key=lambda t: (-t[0], t[1]))

    best_score, _, best_category, best_hits = scored[0]
    runner_up_score = scored[1][0]

    if best_score == 0:
        excerpt = description if len(description) <= 60 else description[:57] + "..."
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"No schema category matches the described problem ('{excerpt}').",
            "flag": "NEEDS_REVIEW",
        }

    cited = ", ".join(f"'{h}'" for h in best_hits[:2])
    reason = f"{best_category}: description cites {cited}"
    if severity_hits:
        reason += f"; urgent due to '{severity_hits[0]}'"

    return {
        "complaint_id": complaint_id,
        "category": best_category,
        "priority": priority,
        "reason": reason + ".",
        "flag": "NEEDS_REVIEW" if runner_up_score == best_score else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on bad rows, always produces output.
    """
    try:
        input_file = open(input_path, newline="", encoding="utf-8")
    except OSError as exc:
        sys.exit(f"error: cannot read input file '{input_path}': {exc}")

    with input_file, open(output_path, "w", newline="", encoding="utf-8") as out_file:
        reader = csv.DictReader(input_file)
        writer = csv.writer(out_file)
        writer.writerow(OUTPUT_COLUMNS)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be processed ({exc}).",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow([result[col] for col in OUTPUT_COLUMNS])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
