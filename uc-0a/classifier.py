"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Enforcement rule 1 -- see agents.md. Matched case-insensitively as substrings,
# which is what makes "child" catch "children" and "hazard" catch "hazards".
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Enforcement rules 4-6 -- see agents.md. Evaluated top to bottom; the first rule
# whose cue appears in the description wins, so the same text always yields the
# same category. Ordering decisions that matter:
#   Pothole before Road Damage    -- a pothole is the more specific defect
#   Streetlight before Heritage   -- "heritage street, lights out" is a lighting
#                                    fault on a heritage street, not damage to a
#                                    heritage structure
#   Flooding before Drain Blockage -- standing water is the citizen-facing
#                                    impact; a blocked drain is the cause
CATEGORY_RULES = [
    ("Pothole",         ["pothole"]),
    ("Streetlight",     ["streetlight", "street light", "lights out"]),
    ("Flooding",        ["flood", "waterlogg", "standing in water"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "manhole", "sewage"]),
    ("Noise",           ["noise", "music", "loudspeaker"]),
    ("Waste",           ["garbage", "waste", "dumped", "dead animal", "refuse"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat", "heatwave"]),
    ("Road Damage",     ["road surface", "cracked", "sinking", "footpath", "tiles"]),
]


def _quote(words):
    """Render matched words as a quoted list so the reason cites source text."""
    return ", ".join("'{}'".format(w) for w in words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority
    """
    text = row.get("description", "").lower()

    # Collect every category whose cues appear, not just the first. More than one
    # match means the complaint is genuinely ambiguous and must be flagged rather
    # than resolved silently (enforcement rule 8).
    matched = []
    for name, cues in CATEGORY_RULES:
        hits = [cue for cue in cues if cue in text]
        if hits:
            matched.append((name, hits))

    if matched:
        category, cues_hit = matched[0]
    else:
        category, cues_hit = "Other", []

    # Enforcement: severity keywords force Urgent, checked before any other
    # priority logic. days_open is deliberately not consulted -- elapsed time is
    # a backlog metric, not a risk signal.
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    priority = "Urgent" if severity_hits else "Standard"

    # Enforcement rule 9: Other is itself a reviewable event.
    # Enforcement rule 8: more than one competing category is too.
    if not matched:
        flag = "NEEDS_REVIEW"
        reason = "No category cue found in the description, so classified Other."
    elif len(matched) > 1:
        flag = "NEEDS_REVIEW"
        competing = " and ".join(name for name, _ in matched)
        reason = "Description cues {} match competing categories {}.".format(
            _quote(cue for _, hits in matched for cue in hits), competing
        )
    else:
        flag = ""
        reason = "Description contains {}.".format(_quote(cues_hit))

    if severity_hits:
        reason += " Priority Urgent: description contains {}.".format(_quote(severity_hits))

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [classify_complaint(row) for row in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
