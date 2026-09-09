"""
UC-0A — Complaint Classifier
Built per agents.md (RICE) + skills.md (classify_complaint, batch_classify).

Enforcement implemented:
 1. Category exact-match from allowed list (no variations / sub-categories).
 2. Priority Urgent on case-insensitive substring severity keywords.
 3. One-sentence reason quoting words from the description.
 4. NEEDS_REVIEW + Other on genuine ambiguity / too little detail.
"""
import argparse
import csv
import os
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

PRIORITIES = ("Urgent", "Standard", "Low")

# agents.md enforcement rule 2 — case-insensitive SUBSTRING match.
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

FLAG_REVIEW = "NEEDS_REVIEW"

# Category signals. Context exclusion: only `description` text is used.
# Short generic words use word boundaries to avoid false hits
# (e.g. "hot" inside "photographing", bare "road" on every pothole row).
CATEGORY_PATTERNS = {
    "Pothole": [r"pothole"],
    "Flooding": [
        r"flood", r"knee-?deep", r"standing in water", r"stranded",
        r"rainwater through", r"channel rainwater",
    ],
    "Streetlight": [
        r"streetlights?", r"street lights?", r"lamp post",
        r"lights out", r"flickering", r"\bunlit\b", r"substation tripped",
        r"\bdarkness\b", r"very dark at night",
    ],
    "Waste": [
        r"garbage", r"waste", r"\bbins?\b", r"overflowing",
        r"dumped", r"dead animal", r"\bpiles?\b", r"not cleared",
        r"not removed", r"smell",
    ],
    "Noise": [
        r"music", r"noise", r"loud", r"amplifier", r"drilling",
        r"wedding", r"\bband\b", r"\bclub\b", r"idling",
    ],
    "Road Damage": [
        r"road surface", r"road collapsed", r"road subsided",
        r"road buckled", r"\bcracked\b", r"\bsinking\b", r"subsidence",
        r"subsided", r"buckled", r"crater", r"manhole",
        r"footpath", r"tiles broken", r"upturned paving",
        r"cobblestones", r"structural concern", r"utility work",
    ],
    "Heritage Damage": [
        r"heritage", r"historic", r"ancient", r"museum",
        r"monument", r"tram road", r"step well", r"old city",
        r"defaced", r"not replaced",
    ],
    "Heat Hazard": [
        r"melting", r"\bheat\w*", r"temperature", r"\d\s?°?c\b",
        r"\bburn\w*", r"\bsun\b", r"\bhot\b", r"heatwave",
        r"sticking", r"bubbling", r"full sun",
    ],
    "Drain Blockage": [
        r"drain", r"stormwater", r"mosquito", r"clogged", r"choked",
    ],
}

# Non-urgent severity: Low only for pure-nuisance Noise / mild Heat
# with no impact language; everything else non-urgent is Standard.
LOW_ELIGIBLE = {"Noise", "Heat Hazard"}
HIGH_IMPACT_RE = re.compile(
    r"risk|unsafe|safety|damage|block|broken|flood|stranded|inaccess|"
    r"health|concern|danger|\bburn\w*|melt|refus|unusable|leak|spark|dark|affected|[4-9]\d",
    re.IGNORECASE,
)

_COMPILED = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
    for cat, pats in CATEGORY_PATTERNS.items()
}


def _is_urgent(description: str) -> bool:
    low = description.lower()
    return any(kw in low for kw in SEVERITY_KEYWORDS)


def _score_categories(description: str) -> dict:
    return {
        cat: sum(1 for rx in rxs if rx.search(description))
        for cat, rxs in _COMPILED.items()
    }


def _quote_words(description: str, max_words: int = 8) -> str:
    """Short quote without sentence terminators (keeps reason one sentence)."""
    text = re.sub(r"\s+", " ", (description or "").strip())
    words = text.split(" ")[:max_words]
    quote = " ".join(words).strip(" ,;:.!?\"'")
    quote = quote.replace(".", "").replace("!", "").replace("?", "")
    if len(text.split(" ")) > max_words:
        quote += "…"
    return quote if quote else "no description provided"


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row (skills.md: classify_complaint)."""
    complaint_id = (row or {}).get("complaint_id", "")
    description = (row or {}).get("description", "")
    if description is None:
        description = ""
    description = str(description)

    # Error handling: missing / empty / too little detail -> Other + NEEDS_REVIEW.
    if not description.strip() or len(description.strip().split()) < 4:
        quote = _quote_words(description) if description.strip() else "no description provided"
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if _is_urgent(description) else "Standard",
            "reason": f"Classified as Other because description states '{quote}'.",
            "flag": FLAG_REVIEW,
        }

    urgent = _is_urgent(description)
    scores = _score_categories(description)
    top_score = max(scores.values())
    top_cats = [c for c, s in scores.items() if s == top_score]

    if top_score == 0 or len(top_cats) > 1:
        # Genuinely ambiguous: fits none or two+ equally -> no false confidence.
        category = "Other"
        flag = FLAG_REVIEW
    else:
        category = top_cats[0]
        flag = ""

    if urgent:
        priority = "Urgent"
    elif category in LOW_ELIGIBLE and not HIGH_IMPACT_RE.search(description):
        priority = "Low"
    else:
        priority = "Standard"

    quote = _quote_words(description)
    reason = f"Classified as {category} with {priority} priority because description states '{quote}'."
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV (skills.md: batch_classify)."""
    with open(input_path, "r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            # Never crash on a bad row; emit a flagged fallback row.
            desc = ""
            try:
                desc = str((row or {}).get("description", ""))
            except Exception:
                desc = ""
            results.append({
                "complaint_id": (row or {}).get("complaint_id", "") if isinstance(row, dict) else "",
                "category": "Other",
                "priority": "Urgent" if _is_urgent(desc) else "Standard",
                "reason": f"Classified as Other because description states '{_quote_words(desc)}'.",
                "flag": FLAG_REVIEW,
            })

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
