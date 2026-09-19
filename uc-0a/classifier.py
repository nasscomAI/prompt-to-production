"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category and priority per the UC-0A schema:
category   -> one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
              Heritage Damage, Heat Hazard, Drain Blockage, Other (exact strings)
priority   -> Urgent (severity keyword present) | Low (minor marker only) | Standard
reason     -> one sentence citing exact words from the description
flag       -> NEEDS_REVIEW on genuine ambiguity / no confident match, else blank

Severity keywords that MUST trigger Urgent:
injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
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

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogging", "water logging",
                 "submerged", "knee-deep", "knee deep", "inaccessible"],
    "Streetlight": ["streetlight", "streetlights", "street light", "street lights",
                    "lights out", "light is out", "no light", "flickering",
                    "sparking", "lamp", "lamps"],
    "Waste": ["garbage", "waste", "bins", "bin", "dumping", "dumped", "litter",
              "dead animal", "debris", "smell", "stagnant water"],
    "Noise": ["music", "noise", "loud", "speaker", "dj", "mic"],
    "Road Damage": ["road surface", "cracked", "cracking", "sinking", "broken tiles",
                    "tiles broken", "upturned", "footpath", "pavement", "road crust"],
    "Heritage Damage": ["heritage", "monument", "ancient", "old city", "heritage street"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "extreme heat", "burning", "sunstroke"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drainage", "manhole",
                       "sewer", "water stagnation", "choked drain"],
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance",
                     "fire", "hazard", "fell", "collapse"]

LOW_MARKERS = ["minor", "cosmetic", "slight", "small crack", "paint fading", "graffiti"]


def _words(text: str) -> list:
    return re.findall(r"[a-z]+", text.lower())


def _find_keywords(pool: list, text: str) -> list:
    lowered = text.lower()
    hits = []
    for kw in pool:
        if _word_boundary_match(kw, lowered):
            hits.append(kw)
    return hits


def _word_boundary_match(keyword: str, lowered_text: str) -> bool:
    pattern = r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])"
    return bool(re.search(pattern, lowered_text))


def _heritage_light_conflict(description: str) -> bool:
    """Heritage context + a lights defect is genuinely ambiguous (both score)."""
    heritage_hits = _find_keywords(CATEGORY_KEYWORDS["Heritage Damage"], description)
    light_hits = _find_keywords(CATEGORY_KEYWORDS["Streetlight"], description)
    return bool(heritage_hits) and bool(light_hits)


def _score(text: str) -> dict:
    scores = {}
    for category in CATEGORIES:
        if category == "Other":
            continue
        hits = _find_keywords(CATEGORY_KEYWORDS[category], text)
        scores[category] = len(hits)
    return scores


def _choose_category(scores: dict):
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], CATEGORIES.index(kv[0])))
    top_cat, top_score = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0
    if top_score == 0:
        return "Other"
    if top_score == runner_up and runner_up > 0:
        return top_cat  # caller uses flag = NEEDS_REVIEW when tied
    return top_cat


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").strip()
    lowered = description.lower()

    scores = _score(description)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], CATEGORIES.index(kv[0])))
    top_score = ranked[0][1]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0
    category = _choose_category(scores)
    if category == "Other":
        category = "Other"

    heritage_light_conflict = _heritage_light_conflict(description)
    if heritage_light_conflict:
        category = "Streetlight"

    severity_hits = _find_keywords(SEVERITY_KEYWORDS, description)
    low_hits = _find_keywords(LOW_MARKERS, description)

    if severity_hits:
        priority = "Urgent"
    elif low_hits:
        priority = "Low"
    else:
        priority = "Standard"

    heritage_light_conflict = _heritage_light_conflict(description)
    flag = "NEEDS_REVIEW" if (top_score == 0 or (top_score == runner_up_score and top_score > 0) or heritage_light_conflict) else ""

    reason = _build_reason(description, category, severity_hits, scores, top_score, runner_up_score, heritage_light_conflict)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(description, category, severity_hits, scores, top_score, runner_up_score, heritage_light_conflict=False):
    lowered = description.lower()
    cat_hits = CATEGORY_KEYWORDS[category] if category in CATEGORY_KEYWORDS else []
    matched_keywords = [kw for kw in cat_hits if _word_boundary_match(kw, lowered)]
    quotes = ", ".join(f"'{w}'" for w in matched_keywords) or "'(none)'"
    if heritage_light_conflict:
        lead = (f"Category {category} selected from '{quotes}' but description also flags "
                f"heritage context - category is ambiguous.")
    elif top_score == 0:
        lead = f"No category keyword matched the description."
    elif top_score == runner_up_score and top_score > 0:
        lead = f"Category {category} selected from '{quotes}' but tied with another category."
    else:
        lead = f"Category {category} selected from keywords {quotes}."
    if severity_hits:
        sev = ", ".join(f"'{w}'" for w in severity_hits)
        lead += f" Priority Urgent because severity word(s) {sev} present."
    else:
        lead += " No severity keyword present -> priority is not Urgent."
    return lead


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row: each failure is logged, the row is skipped,
    and processing continues. Output is still produced for the good rows.
    """
    fieldnames_out = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_out = []
    errors = 0

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for lineno, row in enumerate(reader, start=2):
            try:
                rows_out.append(classify_complaint(row))
            except Exception as exc:
                errors += 1
                print(f"[WARN] Row {lineno} skipped: {exc}")

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames_out)
        writer.writeheader()
        writer.writerows(rows_out)

    if errors:
        print(f"[WARN] {errors} row(s) skipped due to errors.")
    print(f"Wrote {len(rows_out)} rows to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")