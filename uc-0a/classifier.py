"""
UC-0A — Complaint Classifier.
Rule-based classifier implementing classify_complaint + batch_classify
per skills.md, enforced per agents.md (category enum, severity keywords,
reason-with-quote, NEEDS_REVIEW refusal).
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

CATEGORY_PATTERNS = {
    "Pothole": [(r"potholes?", 3), (r"tyre blowout", 2), (r"tyre damage", 2)],
    "Flooding": [(r"flooded", 4), (r"floods", 4),
                 (r"knee-deep", 4), (r"submerged", 3), (r"standing in water", 3),
                 (r"inaccessible", 2), (r"rainwater", 1)],
    "Streetlight": [(r"streetlights?", 3), (r"lights out", 3), (r"unlit", 3),
                    (r"darkness", 3), (r"substation", 2), (r"dark\b", 1)],
    "Waste": [(r"dead animal", 3), (r"garbage", 3), (r"waste", 3), (r"bins?", 3),
              (r"dumped", 3), (r"piles of", 2), (r"overflowing", 1)],
    "Noise": [(r"music", 3), (r"noise", 3), (r"band playing", 3), (r"drilling", 3),
              (r"amplifiers?", 3), (r"idling", 3)],
    "Road Damage": [(r"cracked", 3), (r"sinking", 3), (r"subsided", 3),
                    (r"subsidence", 3), (r"buckled", 3), (r"collapsed", 3),
                    (r"crater", 3), (r"footpath", 3), (r"manhole", 3),
                    (r"upturned", 2), (r"paving", 2)],
    "Heritage Damage": [(r"heritage lamp", 3), (r"heritage stone", 3),
                        (r"heritage residential", 3), (r"heritage building", 3),
                        (r"defaced", 3), (r"cobblestones?", 3), (r"ancient step", 3),
                        (r"historic", 3), (r"tram road", 3)],
    "Heat Hazard": [(r"heatwave", 3), (r"temperatures?", 3), (r"melting", 3),
                    (r"heat", 3), (r"\d+°c", 3), (r"full sun", 3), (r"unbearable", 3),
                    (r"storing heat", 3), (r"bubbling", 3), (r"burns", 3)],
    "Drain Blockage": [(r"drain blocked", 3), (r"drain completely blocked", 3),
                       (r"drain 100% blocked", 3), (r"blocked with", 3),
                       (r"mosquito", 3), (r"stormwater", 2)],
}

SEVERITY_KEYWORDS = [
    (r"injur\w*", "injury"),
    (r"child", "child"),
    (r"school", "school"),
    (r"hospital\w*", "hospital"),
    (r"ambulance", "ambulance"),
    (r"fire", "fire"),
    (r"hazard\w*", "hazard"),
    (r"fell", "fell"),
    (r"collapse\w*", "collapse"),
]

MIN_SCORE = 2


def _matched_phrase(desc: str, category: str) -> str:
    for pattern, _weight in CATEGORY_PATTERNS.get(category, []):
        match = re.search(pattern, desc)
        if match:
            return match.group(0)
    return ""


def _severity_keyword(desc: str) -> str:
    for pattern, name in SEVERITY_KEYWORDS:
        if re.search(pattern, desc):
            return name
    return ""


def _priority(desc: str, row: dict) -> tuple:
    keyword = _severity_keyword(desc)
    if keyword:
        return "Urgent", keyword
    try:
        days_open = int(row.get("days_open", "") or 0)
    except ValueError:
        days_open = 0
    return ("Low" if days_open <= 2 else "Standard"), ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    desc = (description or "").lower()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided — cannot classify",
            "flag": "NEEDS_REVIEW",
        }

    scores = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        score = sum(weight for pattern, weight in patterns if re.search(pattern, desc))
        if score:
            scores[category] = score

    ranked = sorted(scores.items(), key=lambda item: -item[1])
    priority, severity_word = _priority(desc, row)

    if not ranked or ranked[0][1] < MIN_SCORE:
        category, flag = "Other", "NEEDS_REVIEW"
        reason = f"No category keyword matched description '{description[:60]}'"
    elif len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        category, flag = "Other", "NEEDS_REVIEW"
        reason = (f"Tie between {ranked[0][0]} and {ranked[1][0]} — "
                  f"genuinely ambiguous from '{description[:60]}'")
    else:
        category = ranked[0][0]
        flag = ""
        phrase = _matched_phrase(desc, category)
        if severity_word:
            reason = (f"Contains '{phrase}' → {category}; severity keyword "
                      f"'{severity_word}' found in description")
        else:
            reason = f"Contains '{phrase}' → {category}"

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
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"Input CSV not found: {input_path}")
    if not rows:
        raise ValueError(f"Input CSV has no data rows: {input_path}")

    results = []
    failed = 0
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as error:
            failed += 1
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification failed: {error}",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)

    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    flagged = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    counts = {}
    for r in results:
        counts[r["category"]] = counts.get(r["category"], 0) + 1

    print(f"Classified {len(results)} rows ({failed} failed, 0 crashed) → {output_path}")
    print(f"Urgent: {urgent} · NEEDS_REVIEW: {flagged}")
    print("Categories: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")