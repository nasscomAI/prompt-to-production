"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re


CATEGORY_RULES = [
    (
        "Flooding",
        [
            r"\bflood\w*\b",
            r"\bflooded\b",
            r"\bflooding\b",
            r"\binundat\w*\b",
            r"\bwaterlogged\b",
            r"\bwater\b",
            r"\bsubmerged\b",
        ],
    ),
    (
        "Drain Blockage",
        [
            r"\bdrain\w*\b.*\bblock\w*\b",
            r"\bblock\w*\b.*\bdrain\w*\b",
            r"\bstormwater drain\b",
            r"\bmanhole\b.*\bblock\w*\b",
            r"\bblocked drain\b",
        ],
    ),
    (
        "Streetlight",
        [
            r"\bstreetlight\w*\b",
            r"\blight\w*\b.*\bout\b",
            r"\bunlit\b",
            r"\bflicker\w*\b",
            r"\bspark\w*\b",
            r"\blamp post\b",
            r"\bdarkness\b",
            r"\bsubstation tripped\b",
        ],
    ),
    (
        "Heat Hazard",
        [
            r"\bheat\w*\b",
            r"\btemperature\b",
            r"\b\d{2,3}°c\b",
            r"\bmelt\w*\b",
            r"\bburn\w*\b",
            r"\bscorch\w*\b",
            r"\bunsafe\b.*\bheat\b",
        ],
    ),
    (
        "Heritage Damage",
        [
            r"\bheritage\b.*\b(defac\w*|damag\w*|knock\w*|broken|not replaced|removed)\b",
            r"\bhistoric\w*\b.*\b(defac\w*|damag\w*|broken|removed|not replaced)\b",
            r"\bold city\b.*\b(defac\w*|damag\w*|broken|removed|not replaced)\b",
            r"\bcobbleston\w*\b.*\bbroken\b",
            r"\bheritage zone\b",
        ],
    ),
    (
        "Pothole",
        [
            r"\bpothole\w*\b",
            r"\btyre\b.*\bdamag\w*\b",
            r"\bwheel\b.*\bswallow\w*\b",
            r"\bcrater\b",
            r"\bdeep hole\b",
        ],
    ),
    (
        "Road Damage",
        [
            r"\broad\b.*\b(crack\w*|subsiden\w*|sink\w*|collapse\w*|buckl\w*|bubbl\w*|damag\w*)\b",
            r"\bfootpath\b.*\b(broken|sink\w*|subsiden\w*|upturned|damag\w*|crack\w*)\b",
            r"\bsurface\b.*\b(crack\w*|sink\w*|subsiden\w*|buckl\w*|damag\w*)\b",
            r"\bpaving\b.*\b(broken|removed|upturned)\b",
            r"\bbridge approach\b.*\b(subsiden\w*|damag\w*|collapse\w*)\b",
            r"\bmanhole cover\b.*\b(missing|broken|open|damag\w*)\b",
            r"\bcover missing\b",
        ],
    ),
    (
        "Waste",
        [
            r"\bwaste\b",
            r"\bgarbage\b",
            r"\btrash\b",
            r"\bbin\w*\b.*\boverflow\w*\b",
            r"\blitter\b",
            r"\bdead animal\b",
            r"\brubbish\b",
        ],
    ),
    (
        "Noise",
        [
            r"\bnoise\b",
            r"\bmusic\b",
            r"\bamplifier\w*\b",
            r"\bdrilling\b",
            r"\bidling\b",
            r"\bloud\b",
            r"\bdisturb\w*\b",
        ],
    ),
]

SEVERITY_KEYWORDS = [
    "injury",
    "injured",
    "child",
    "children",
    "school",
    "hospital",
    "hospitalised",
    "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _match_snippets(text: str, patterns: list[str]) -> list[str]:
    matches = []
    for pattern in patterns:
        if re.search(pattern, text):
            matches.append(pattern)
    return matches


def _score_categories(description: str) -> tuple[str, bool, list[str]]:
    text = _normalize_text(description)
    scored = []
    category_order = [name for name, _ in CATEGORY_RULES]
    for category, patterns in CATEGORY_RULES:
        matches = _match_snippets(text, patterns)
        if matches:
            scored.append((category, len(matches), matches))

    if not scored:
        return "Other", True, []

    scored.sort(key=lambda item: (-item[1], category_order.index(item[0])))
    top_score = scored[0][1]
    top_matches = [item for item in scored if item[1] == top_score]
    category = top_matches[0][0]
    flag = len(top_matches) > 1
    evidence = top_matches[0][2]
    return category, flag, evidence


def _build_reason(category: str, description: str, evidence: list[str], priority: str) -> str:
    text = description.strip() if description else ""
    if not text:
        return "Description was missing, so the row was classified conservatively."

    snippets = []
    for pattern in evidence[:2]:
        found = re.search(pattern, text, flags=re.IGNORECASE)
        if found:
            snippets.append(found.group(0))
    if not snippets:
        snippets.append(text[:80].rstrip())

    joined = " and ".join(f'"{snippet}"' for snippet in snippets)
    return f"Mentions {joined}, so this is {category} with {priority} priority."


def _determine_priority(description: str, category: str) -> str:
    text = _normalize_text(description)
    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        return "Urgent"
    if category in {"Noise", "Waste"}:
        return "Low"
    return "Standard"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = row.get("description", "") or ""
    category, needs_review, evidence = _score_categories(description)
    priority = _determine_priority(description, category)
    reason = _build_reason(category, description, evidence, priority)
    flag = "NEEDS_REVIEW" if needs_review else ""

    return {
        "complaint_id": row.get("complaint_id", "") or "",
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, newline="", encoding="utf-8-sig") as input_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row could not be classified because of an internal error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
