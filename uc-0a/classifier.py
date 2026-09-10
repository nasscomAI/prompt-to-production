"""
UC-0A — Complaint Classifier

Rule-based implementation of the enforcement rules in agents.md.
Implements the two skills in skills.md:
  - classify_complaint: one complaint row in -> category + priority + reason + flag out
  - batch_classify: reads input CSV, applies classify_complaint per row, writes output CSV

Classification only: never edits the input, never invents categories, and only
labels rows.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": [
        "flood", "waterlog", "submerged", "knee-deep", "knee deep",
        "standing water", "standing in water", "inaccessible",
        "channel rainwater",
    ],
    "Streetlight": [
        "streetlight", "street light", "lights", "lamp", "unlit", "darkness",
    ],
    "Waste": [
        "garbage", "waste", "rubbish", "trash", "litter", "bins",
        "dumped", "dead animal", "refuse",
    ],
    "Noise": [
        "noise", "music", "loud", "honking", "amplifier", "drilling",
        "idling", "band playing",
    ],
    "Road Damage": [
        "road surface", "road collapsed", "road buckled", "cracked", "crack",
        "sinking", "sunk", "subsidence", "subsided", "manhole", "upturned",
        "paving", "footpath", "tiles", "pavement", "cobblestone", "crater",
    ],
    "Heritage Damage": ["heritage", "monument", "historic", "ancient"],
    "Heat Hazard": [
        "heat", "heatwave", "temperature", "melting", "full sun", "\u00b0c",
    ],
    "Drain Blockage": ["drain", "blocked", "clogged", "sewer"],
}

SEVERITY_KEYWORDS = [
    "injur", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _score_categories(description: str) -> dict:
    """Return a dict mapping each category to the number of keyword hits."""
    text = description.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text)
    return scores


def _sentence_around(text: str, keyword: str) -> str:
    """Return the sentence of `text` containing `keyword`, else the whole text."""
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        if keyword in sentence.lower():
            return sentence.strip()
    return text.strip()


def _first_keyword_hit(description: str, category: str) -> str:
    """Return the first matching keyword for a category in the description."""
    text = description.lower()
    for kw in CATEGORY_KEYWORDS.get(category, []):
        if kw in text:
            return kw
    return description[:20]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Handle empty descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided to classify.",
            "flag": "NEEDS_REVIEW",
        }

    # Score each category by keyword hits
    scores = _score_categories(description)
    ranked = sorted(scores.items(), key=lambda item: item[1])
    top_category, top_score = ranked[-1]
    second_score = ranked[-2][1] if len(ranked) >= 2 else 0
    tied = [cat for cat, score in scores.items() if score == top_score and score > 0]

    # Check severity keywords for priority
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in description.lower()]
    priority = "Urgent" if severity_hits else "Standard"

    # Determine category, reason, and flag
    flagged = []
    if top_score == 0:
        # No keyword matched any category
        category, flag = "Other", "NEEDS_REVIEW"
        snippet = description if len(description) <= 120 else description[:120] + "..."
        reason = f'No category keyword found in "{snippet}".'
    elif len(tied) > 1:
        # Genuinely ambiguous — multiple categories tied
        category, flag = "Other", "NEEDS_REVIEW"
        snippet = _sentence_around(description, tied[0])
        reason = (
            f'"{snippet}" supports both {tied[0]} and {tied[1]}, '
            "so no single category can be determined."
        )
    else:
        category = top_category
        snippet = _sentence_around(description, _first_keyword_hit(description, top_category))
        if second_score > 0 and top_score - second_score <= 1:
            # Close runner-up — flag for review
            flag = "NEEDS_REVIEW"
            runner_up = [c for c, s in scores.items() if s == second_score and s > 0][0]
            flagged.append(f"also supports {runner_up}")
        else:
            flag = ""

    # Build reason string
    if severity_hits and top_score > 0 and flag == "":
        reason = (
            f'"{snippet}" indicates {category} and contains severity keyword '
            f'"{severity_hits[0]}".'
        )
    elif top_score > 0 and flag == "":
        reason = f'"{snippet}" indicates {category}.'
    elif flagged:
        reason = f'"{snippet}" indicates {category}; {flagged[0]}, needs review.'

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # never abort the batch on one bad row
            results.append({
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row could not be classified: {exc}.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
