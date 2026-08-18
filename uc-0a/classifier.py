"""
UC-0A — Complaint Classifier

Implements agents.md + skills.md:
  - classify_complaint: one row -> category + priority + reason + flag
  - batch_classify:     CSV -> results CSV, never crashes on bad rows
"""
import argparse
import csv
import re

CATEGORY_PATTERNS = {
    "Heritage Damage": [
        r"defaced",
        r"heritage stone",
        r"historic[^.]*cobblestone",
        r"heritage[^.]*build",
        r"ancient step well",
        r"heritage concern",
    ],
    "Heat Hazard": [
        r"heat",
        r"\btemperature",
        r"melting",
        r"bubbling",
        r"scorching",
        r"\bsun\b",
        r"unbearable",
        r"\d+°",
    ],
    "Pothole": [r"pothole"],
    "Flooding": [
        r"flood",
        r"water.?logging",
        r"standing water",
        r"rainwater",
        r"inundat",
    ],
    "Drain Blockage": [
        r"drain",
        r"drainage",
        r"sewer",
        r"blocked",
        r"blockage",
        r"choked",
    ],
    "Streetlight": [
        r"streetlight",
        r"street light",
        r"lights out",
        r"lamp post",
        r"lamppost",
        r"streetlamp",
        r"flicker",
        r"spark",
        r"unlit",
        r"substation",
        r"wiring",
        r"\bdark\b",
    ],
    "Noise": [
        r"noise",
        r"noisy",
        r"music",
        r"\bband\b",
        r"loud",
        r"speaker",
        r"amplifier",
        r"drilling",
        r"idling",
        r"\bhorn\b",
    ],
    "Waste": [
        r"garbage",
        r"waste",
        r"rubbish",
        r"trash",
        r"litter",
        r"dead animal",
        r"overflow",
        r"not cleared",
        r"dumped",
        r"refuse",
    ],
    "Road Damage": [
        r"road surface",
        r"cracked",
        r"sinking",
        r"subsid",
        r"buckled",
        r"manhole",
        r"footpath",
        r"pavement",
        r"paving",
        r"cobblestone",
        r"tiles",
        r"upturned",
        r"crater",
        r"road collapse",
    ],
}

URGENT_PATTERNS = [
    r"\binjur(?:y|ies|ed)\b",
    r"\bchild(?:ren)?\b",
    r"\bschool\b",
    r"\bhospital",
    r"\bambulance",
    r"\bfire\b",
    r"\bhazard",
    r"\bfell\b",
    r"\bcollapse",
]

TRIVIAL_PATTERNS = [
    r"\bminor\b",
    r"\bcosmetic\b",
    r"\bself.?resolving\b",
    r"single flickering",
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _earliest(patterns: list, text: str):
    best = None
    for p in patterns:
        m = re.search(p, text)
        if m and (best is None or m.start() < best.start()):
            best = m
    return best


def _detect_category(text: str):
    for cat in ("Heritage Damage", "Heat Hazard", "Pothole"):
        m = _earliest(CATEGORY_PATTERNS[cat], text)
        if m:
            return cat, m

    flood_m = _earliest(CATEGORY_PATTERNS["Flooding"], text)
    drain_m = _earliest(CATEGORY_PATTERNS["Drain Blockage"], text)
    if flood_m or drain_m:
        if flood_m and drain_m:
            if flood_m.start() <= drain_m.start():
                return "Flooding", flood_m
            return "Drain Blockage", drain_m
        if flood_m:
            return "Flooding", flood_m
        return "Drain Blockage", drain_m

    for cat in ("Streetlight", "Noise", "Waste", "Road Damage"):
        m = _earliest(CATEGORY_PATTERNS[cat], text)
        if m:
            return cat, m

    return "Other", None


def _detect_priority(text: str):
    urgent_m = _earliest(URGENT_PATTERNS, text)
    if urgent_m:
        return "Urgent", urgent_m
    if _earliest(TRIVIAL_PATTERNS, text):
        return "Low", None
    return "Standard", None


def _sentence_containing(description: str, match) -> str:
    if match is None:
        return ""
    start = match.start()
    left = description.rfind(".", 0, start) + 1
    right = description.find(".", start)
    if right == -1:
        right = len(description)
    return description[left:right].strip(" ")


def _build_reason(description: str, category: str, cat_match, priority: str, urgent_match) -> str:
    if category == "Other":
        fragment = description[:70].strip()
        return f"Category unclear from description: '{fragment}'; flagging NEEDS_REVIEW."
    quoted = _sentence_containing(description, cat_match)
    if priority == "Urgent" and urgent_match:
        uw = description[urgent_match.start():urgent_match.end()]
        return f"Category {category}, priority {priority} because description contains: '{quoted}' and '{uw}'."
    return f"Category {category}, priority {priority} because description contains: '{quoted}'."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty or missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    category, cat_match = _detect_category(text)
    priority, urgent_match = _detect_priority(text)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    reason = _build_reason(description, category, cat_match, priority, urgent_match)
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
    Never crashes on a bad row: each row is classified independently and a
    row that cannot be classified becomes Other + NEEDS_REVIEW.
    """
    with open(input_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    results = []
    for idx, row in enumerate(rows):
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "complaint_id": row.get("complaint_id", f"row_{idx}"),
                "category": "Other",
                "priority": "Standard",
                "reason": "Row could not be classified.",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
