"""
UC-0A — Complaint Classifier
Deterministic rule engine implementing the RICE enforcement in agents.md and
the skill contracts in skills.md.
"""
import argparse
import csv
import re
import sys

CATEGORY_ORDER = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlog", "water logging", "standing water", "inundat"],
    "Streetlight": ["streetlight", "street light", "streetlamp", "lamp post", "light pole", "lights out"],
    "Waste": ["garbage", "waste", "litter", "trash", "rubbish", "dumped", "dead animal"],
    "Noise": ["noise", "noisy", "loud", "loudspeaker", "music"],
    "Road Damage": ["cracked", "cracks", "sinking", "sinkhole", "upturned", "tiles broken", "footpath", "broken road", "damaged road", "subsid"],
    "Heritage Damage": ["heritage", "monument", "statue", "mural"],
    "Heat Hazard": ["heatwave", "heat wave", "extreme heat", "heatstrok"],
    "Drain Blockage": ["drain", "clogged", "choked", "sewer", "blocked drain", "drain blocked"],
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

LOW_PRIORITY_HINTS = re.compile(r"\b(minor|slight|not urgent)\b", re.IGNORECASE)


def _find_evidence(description: str, keywords: list) -> list:
    """Return the actual substrings of `description` that match any keyword."""
    found = []
    for kw in keywords:
        match = re.search(re.escape(kw), description, re.IGNORECASE)
        if match:
            found.append(match.group(0))
    return found


def _error_result(complaint_id: str, reason: str) -> dict:
    return {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": reason,
        "flag": "NEEDS_REVIEW",
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement mapping (agents.md):
      - exact taxonomy strings only
      - severity keywords force priority Urgent
      - reason cites specific words from the description
      - genuine ambiguity -> Other/closest category + NEEDS_REVIEW
      - null/unreadable description -> Other + NEEDS_REVIEW, never crash
    """
    if not isinstance(row, dict):
        row = {}
    raw_description = row.get("description")
    description = str(raw_description).strip() if raw_description is not None else ""
    complaint_id = str(row.get("complaint_id") or "").strip()

    if not description:
        return _error_result(
            complaint_id,
            "Description missing or unreadable, so defaulted to Other pending review.",
        )

    # --- Category scoring -------------------------------------------------
    scores = {}
    evidence = {}
    for category in CATEGORY_ORDER:
        hits = _find_evidence(description, CATEGORY_KEYWORDS[category])
        if hits:
            scores[category] = len(hits)
            evidence[category] = hits

    if not scores:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": _assign_priority(description),
            "reason": "No taxonomy indicator found in description, so defaulted to Other pending review.",
            "flag": "NEEDS_REVIEW",
        }

    top_score = max(scores.values())
    leaders = [c for c in CATEGORY_ORDER if scores.get(c) == top_score]
    ambiguous = len(leaders) > 1
    category = leaders[0]  # tie-break: canonical schema order

    # --- Priority ---------------------------------------------------------
    severity_hits = _find_evidence(description, SEVERITY_KEYWORDS)
    priority = _assign_priority(description, severity_hits)

    # --- Reason (one sentence, citing specific description words) ----------
    citations = ", ".join(f"'{e}'" for e in evidence[category])
    parts = [f"description mentions {citations} indicating {category}"]
    if severity_hits and priority == "Urgent":
        sev_citations = ", ".join(f"'{e}'" for e in severity_hits)
        parts.append(f"priority Urgent because {sev_citations} signals a safety risk")
    elif priority == "Low":
        parts.append("no urgency indicators and wording suggests a minor issue")
    reason = "; ".join(parts)
    flag = ""
    if ambiguous:
        others = ", ".join(c for c in leaders[1:])
        reason += f"; ambiguous with {others} ({', '.join(evidence[c][0] for c in leaders[1:])}) so flagged for review"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason + ".",
        "flag": flag,
    }


def _assign_priority(description: str, severity_hits: list = None) -> str:
    """Urgent if any severity keyword present, else Standard/Low."""
    if severity_hits is None:
        severity_hits = _find_evidence(description, SEVERITY_KEYWORDS)
    if severity_hits:
        return "Urgent"
    if LOW_PRIORITY_HINTS.search(description):
        return "Low"
    return "Standard"


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Contract (skills.md): one output row per input row with header
    complaint_id,category,priority,reason,flag. Missing input file exits early
    with a clear message and writes no output. A bad row never aborts the batch.
    """
    try:
        input_file = open(input_path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print(f"Error: cannot read input file '{input_path}': {exc}")
        sys.exit(1)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    flagged = 0
    processed = 0
    with input_file, open(output_path, "w", newline="", encoding="utf-8") as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # final safety net: batch must complete
                result = _error_result(
                    str(row.get("complaint_id") or "") if isinstance(row, dict) else "",
                    f"Classification failed internally ({exc}), defaulted to Other pending review.",
                )
            if result["flag"] == "NEEDS_REVIEW":
                flagged += 1
            writer.writerow(result)
            processed += 1

    print(f"Done. Classified {processed} rows ({flagged} flagged NEEDS_REVIEW). Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
