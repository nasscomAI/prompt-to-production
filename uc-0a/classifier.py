#!/usr/bin/env python3
"""UC-0A Complaint Classifier — deterministic keyword-based classification."""

import argparse
import csv
import os
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Each category maps to a list of regex patterns (word-boundary anchored).
# Longer/more-specific patterns are listed first so they match before substrings.
CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpotholes?\b",
        r"\broad\s+hole\b",
        r"\broad\s+pit\b",
    ],
    "Flooding": [
        r"\bwater\s*logged\b",
        r"\bwater\s*logging\b",
        r"\bchannel\s+rainwater\b",
        r"\bfloods?\b",
        r"\bflooded\b",
        r"\bflooding\b",
        r"\bsubmerged\b",
        r"\bunderwater\b",
        r"\brainwater\b",
    ],
    "Streetlight": [
        r"\bstreet\s*lights?\b",
        r"\blamp\s*post\b",
        r"\blampp?ost\b",
        r"\bunlit\b",
        r"\blights?\s+out\b",
        r"\bflickering\b",
        r"\blighting\b",
        r"\bdark\s+at\s+night\b",
        r"\bdarkness\b",
        r"\blighting\b",
        r"\bdark\b",
    ],
    "Waste": [
        r"\bdead\s+animal\b",
        r"\bgarbage\b",
        r"\btrash\b",
        r"\brubbish\b",
        r"\bnot\s+cleared\b",
        r"\bbins?\b",
        r"\boverflowing\b",
        r"\bwaste\b",
        r"\bhealth\s+risk\b",
    ],
    "Noise": [
        r"\bwedding\s+band\b",
        r"\bband\s+playing\b",
        r"\bamplifiers?\b",
        r"\bdrilling\b",
        r"\bidling\b",
        r"\bengines?\b",
        r"\bclub\s+music\b",
        r"\bnoise\b",
        r"\bmusic\b",
        r"\bloud\b",
        r"\baudible\b",
    ],
    "Road Damage": [
        r"\broad\s+(?:damage|cracked|surface)\b",
        r"\bsurface\s+(?:bubbling|cracked)\b",
        r"\broad\s+collapsed\b",
        r"\broad\s+subsided\b",
        r"\broad\s+sinking\b",
        r"\broad\s+cracked\b",
        r"\broad\s+buckled\b",
        r"\bcollapsed\b",
        r"\bsubsided\b",
        r"\bsubsidence\b",
        r"\bbuckled\b",
        r"\bsinking\b",
        r"\bcracked\b",
        r"\bfootpath\b",
        r"\bupturned\b",
        r"\bpaving\b",
        r"\btarmac\b",
        r"\bcobblestones\b",
        r"\bbroken\b",
    ],
    "Heritage Damage": [
        r"\bheritage\s+(?:zone|area|street|stone|building|precinct|residential|lamp\s*post)\b",
        r"\bheritage\b",
        r"\bhistoric(?:al)?\b",
        r"\bancient\b",
    ],
    "Heat Hazard": [
        r"\bheat\s*wave\b",
        r"\bheatwave\b",
        r"\btemperature(?:s)?\b",
        r"\bcelsius\b",
        r"\b°\s*c\b",
        r"\bdangerous\s+temperature\b",
        r"\bunbearable\b",
        r"\bmelting\b",
        r"\bburns?\b",
        r"\bheat\b",
    ],
    "Drain Blockage": [
        r"\bstormwater\s+drain\b",
        r"\bdrain\s+completely\s+blocked\b",
        r"\bblocked\s+drain\b",
        r"\bdrain\s+blocked\b",
        r"\bdrainage\b",
        r"\bdraining\b",
        r"\bconstruction\s+debris\b",
    ],
}

# Conflict pairs: if both categories have matches, it's ambiguous.
CONFLICT_PAIRS = [
    ("Heritage Damage", "Streetlight"),
    ("Heritage Damage", "Road Damage"),
    ("Heritage Damage", "Waste"),
    ("Heritage Damage", "Noise"),
    ("Flooding", "Drain Blockage"),
    ("Pothole", "Flooding"),
    ("Road Damage", "Heat Hazard"),
]


def _score_category(description_lower: str, patterns: list) -> int:
    """Count unique regex matches in description for a category's patterns."""
    matched = set()
    for pat in patterns:
        for m in re.finditer(pat, description_lower):
            # Use the match span to deduplicate overlapping matches
            matched.add(m.span())
    return len(matched)


def classify_complaint(description: str) -> dict:
    """Classify a single complaint. Returns dict with category, priority, reason, flag."""
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # --- Step 1: score categories (deduplicated regex matches) ---
    scores = {}
    for cat, patterns in CATEGORY_PATTERNS.items():
        score = _score_category(desc_lower, patterns)
        if score > 0:
            scores[cat] = score

    # --- Step 2: pick category with conflict detection ---
    if not scores:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        sorted_cats = sorted(scores.items(), key=lambda x: -x[1])
        best_score = sorted_cats[0][1]
        top_cats = [c for c, s in sorted_cats if s == best_score]

        # Check if top two categories form a known conflict pair
        conflict_flag = False
        if len(sorted_cats) >= 2:
            top_two = set(c for c, s in sorted_cats[:2])
            for ca, cb in CONFLICT_PAIRS:
                if {ca, cb} == top_two or (ca in top_two and cb in top_two):
                    conflict_flag = True
                    break

        # Also check: if any conflict pair has one winner and one close second
        if not conflict_flag and len(sorted_cats) >= 2:
            for ca, cb in CONFLICT_PAIRS:
                if ca in scores and cb in scores:
                    # Both present in scores — ambiguous
                    conflict_flag = True
                    break

        if len(top_cats) > 1 or conflict_flag:
            category = top_cats[0]
            flag = "NEEDS_REVIEW"
        else:
            category = top_cats[0]
            flag = ""

    # --- Step 3: priority ---
    has_severity = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"

    # --- Step 4: reason ---
    cited = _cite_description(description, category)
    reason = f"{category} issue reported: {cited}."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _cite_description(description: str, category: str) -> str:
    """Extract a short citation from the original description."""
    candidates = []
    words = description.split()

    keyword_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["light", "unlit", "dark", "lamp"],
        "Waste": ["waste", "garbage", "bin", "animal"],
        "Noise": ["noise", "music", "drill", "amplifier", "idling", "band", "engine"],
        "Road Damage": ["road", "cracked", "sinking", "subsided", "collapsed",
                        "buckled", "footpath", "broken", "paving", "surface"],
        "Heritage Damage": ["heritage", "historic", "ancient"],
        "Heat Hazard": ["heat", "°c", "celsius", "temperature", "melting", "burn"],
        "Drain Blockage": ["drain", "drainage"],
        "Other": [],
    }

    triggers = keyword_map.get(category, [])

    for i, w in enumerate(words):
        wl = w.lower().rstrip(".,;:!?")
        if any(k in wl for k in triggers):
            start = max(0, i - 1)
            end = min(len(words), i + 3)
            candidates.append(" ".join(words[start:end]))

    if candidates:
        citation = max(candidates, key=len).rstrip(".,;:!")
        return citation

    first_words = description.split()[:8]
    return " ".join(first_words).rstrip(".,;:!")


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write output CSV."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    for row in rows:
        desc = row.get("description", "")
        result = classify_complaint(desc)
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows → {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
