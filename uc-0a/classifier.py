"""
UC-0A — Complaint Classifier
Built from uc-0a/agents.md and uc-0a/skills.md.
"""
import argparse
import csv

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
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": {"pothole": 2},
    "Flooding": {"flood": 2, "waterlog": 2, "water logging": 2, "rainwater": 1},
    "Streetlight": {"streetlight": 2, "lights out": 2, "light out": 2, "lamp post": 2, "unlit": 2},
    "Waste": {"garbage": 2, "waste": 2, "litter": 2, "debris": 2, "dead animal": 2, "bins": 2},
    "Noise": {"music": 2, "band playing": 2, "amplifier": 2, "noise": 2, "loud": 2, "horn": 2, "drilling": 2, "idling": 2},
    "Road Damage": {
        "cracked": 2, "sinking": 2, "buckled": 2, "subsided": 2, "subsidence": 2,
        "collapsed": 2, "crater": 2, "manhole": 2, "broken": 1, "road": 1,
        "footpath": 1, "tiles": 1, "paving": 1,
    },
    "Heritage Damage": {"heritage": 2, "defaced": 2},
    "Heat Hazard": {"heat": 2, "temperature": 2, "melting": 2, "bubbling": 2, "sunstroke": 2},
    "Drain Blockage": {"drain": 2, "blocked": 2, "choked": 2, "sewer": 2, "clogged": 2},
    "Other": {},
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _actual_phrase(description: str, keyword: str) -> str:
    """
    Locate the keyword (case-insensitive) in the description and return the
    full surrounding word/phrase exactly as written in the description.
    """
    low = description.lower()
    idx = low.find(keyword)
    if idx == -1:
        return keyword
    start, end = idx, idx + len(keyword)
    while start > 0 and description[start - 1].isalnum():
        start -= 1
    while end < len(description) and description[end].isalnum():
        end += 1
    return description[start:end]


def _score_category(description: str):
    """
    Score every allowed category by weighted keyword hits.
    Returns dict: category -> {"score": int, "words": [actual phrases]}.
    """
    text = description.lower()
    result = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        words = []
        for keyword, weight in keywords.items():
            if keyword in text:
                score += weight
                words.append(_actual_phrase(description, keyword))
        result[category] = {"score": score, "words": words}
    return result


def _classify_category(description: str):
    """
    Returns (category, flag, scored) where flag is NEEDS_REVIEW when the
    category is genuinely ambiguous (top categories tie) or nothing fits.
    """
    scored = _score_category(description)
    top_score = max(s["score"] for s in scored.values())
    winners = [c for c, s in scored.items() if s["score"] == top_score]

    if top_score == 0 or len(winners) > 1:
        return "Other", "NEEDS_REVIEW", scored
    return winners[0], "", scored


def _quote_words(words, limit=2):
    return ", ".join('"' + w + '"' for w in words[:limit])


def _reason_for(description: str, category: str, flag: str, scored: dict) -> str:
    if category != "Other":
        words = scored[category]["words"]
        quoted = _quote_words(words)
        if len(words) <= 1:
            return f"Category \"{category}\" fits because the description says {quoted}."
        return f"Category \"{category}\" fits because the description says {quoted}."

    tied = sorted(
        (c for c in CATEGORIES if c != "Other" and scored[c]["score"] > 0),
        key=lambda c: (-scored[c]["score"], c),
    )
    if tied:
        parts = []
        for c in tied[:2]:
            parts.append(f"{_quote_words(scored[c]['words'])} (suggesting {c})")
        joined = " and ".join(parts)
        return (
            f"Category is ambiguous because the description says {joined}; "
            f"this needs review."
        )

    snippet = " ".join(description.split()[:3])
    return f"No allowed category fits the description \"{snippet}\"; this needs review."


def _priority_for(description: str) -> str:
    text = description.lower()
    if any(kw in text for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


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
            "reason": "The description is blank, so no category can be determined; this needs review.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag, scored = _classify_category(description)
    priority = _priority_for(description)
    reason = _reason_for(description, category, flag, scored)
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
    Skips malformed rows with a warning; never crashes the whole run.
    """
    results = []
    skipped = 0
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for line_num, row in enumerate(reader, start=2):
            try:
                if row is None or not (row.get("complaint_id") or "").strip():
                    raise ValueError("row has no complaint_id")
                results.append(classify_complaint(row))
            except Exception as exc:
                skipped += 1
                print(f"Warning: skipped input line {line_num}: {exc}")

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints ({skipped} skipped).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
