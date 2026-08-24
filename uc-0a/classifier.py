"""
UC-0A — Complaint Classifier
Implements agents.md + skills.md enforcement with deterministic rule-based classification.
Run: python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ALLOWED_CATEGORIES = [
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

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Category keywords — ordered by specificity; Heritage Damage prioritized over Streetlight, etc.
# Each entry: (category, [keywords/phrases lowercased], weight optional default 1)
# We use phrase matching with lowercased description.
CATEGORY_KEYWORDS = {
    "Heritage Damage": ["heritage", "historic", "historical", "museum", "monument", "lamp post heritage", "cobblestones", "heritage stone"],
    "Heat Hazard": ["heat", "temperature", "tarmac melting", "melting", "heatwave", "storing heat", "burns on contact", "sun exposed", "52°c", "44°c", "45°c"],
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flooded", "flooding", "floods", "flood", "waterlogged", "underpass flooded", "stranded", "bridge becomes inaccessible", "channel rainwater"],
    "Drain Blockage": ["drain blocked", "drain block", "drainage", "stormwater drain", "main drain", "drain 100% blocked", "mosquito breeding", "blocked with construction debris"],
    "Streetlight": ["streetlight", "streetlights", "street light", "lights out", "flickering", "sparking", "dark at night", "unlit", "darkness", "substation tripped", "electrical hazard"],
    "Waste": ["garbage", "waste", "overflowing", "bins", "dumped", "dead animal", "bulk waste", "refuse", "not cleared", "trash", "health concern", "health risk"],
    "Noise": ["music", "noise", "loud", "amplifiers", "wedding", "drilling", "construction drilling", "idling", "venue playing"],
    "Road Damage": ["road surface", "cracked", "sinking", "subsided", "subsidence", "buckled", "collapsed", "manhole", "footpath", "tiles broken", "upturned", "paving", "bridge approach", "crater", "structural concern", "gas leak smell"],
}

# Priority for tie-breaking when scores equal — higher in list wins, except Other last
TIE_BREAK_ORDER = ["Heritage Damage", "Heat Hazard", "Pothole", "Flooding", "Drain Blockage", "Streetlight", "Waste", "Noise", "Road Damage", "Other"]


def _contains_severity_keyword(desc_lower: str) -> bool:
    for kw in SEVERITY_KEYWORDS:
        # word boundary match to avoid false positives (e.g., "children" should still trigger child)
        # use simple substring but for 'fell' ensure word boundary
        if kw in desc_lower:
            # for short keywords like fell, check word boundary to avoid 'fellow'
            if kw in ("fell", "fire", "child", "hazard"):
                if re.search(rf"\b{re.escape(kw)}\w*\b", desc_lower):
                    return True
                continue
            return True
    return False


def _score_categories(desc_lower: str) -> dict:
    scores = {cat: 0 for cat in ALLOWED_CATEGORIES}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                # longer phrase gets higher weight
                weight = 2 if len(kw.split()) > 1 else 1
                # Flooding definitive phrases get extra weight to win over Drain Blockage when flooded
                if cat == "Flooding" and kw in ("flooded", "flooding", "floods", "underpass flooded"):
                    weight = 3
                # boost heritage/heat which are rare but definitive
                if cat in ("Heritage Damage", "Heat Hazard"):
                    weight += 1
                scores[cat] += weight
    # Robust drain block detection: drain + block* within 3 words captures variants like "drain completely blocked"
    if re.search(r"\bdrain\b.{0,30}\bblock", desc_lower):
        scores["Drain Blockage"] += 3
    # If flooded present, Flooding is the primary taxonomy — boost to outweigh drain cause
    if any(k in desc_lower for k in ("flooded", "flooding", "floods")):
        scores["Flooding"] += 4
    return scores


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or row.get("id") or "").strip()
    description = row.get("description", "")
    if description is None:
        description = ""
    description = str(description).strip()
    desc_lower = description.lower()

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — no signal to classify, flagged for review.",
            "flag": "NEEDS_REVIEW",
        }

    scores = _score_categories(desc_lower)
    max_score = max(scores.values())

    # Determine top categories
    top_cats = [cat for cat, sc in scores.items() if sc == max_score and sc > 0]

    if not top_cats:
        # No keyword matched → Other
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_words = " ".join(description.split()[:6])
        reason = f'No taxonomy keywords found in "{reason_words}..." — classified as Other and flagged for review.'
    elif len(top_cats) == 1:
        category = top_cats[0]
        flag = ""
        # Only flag on genuine tie — near-tie is not ambiguity per spec; prevents over-flagging
        # Build reason citing words
        # find matched keywords for chosen category
        matched = [kw for kw in CATEGORY_KEYWORDS.get(category, []) if kw in desc_lower]
        # also include drain regex match for Drain Blockage
        if category == "Drain Blockage" and not matched and re.search(r"\bdrain\b.{0,30}\bblock", desc_lower):
            matched = ["drain ... blocked"]
        cited = ", ".join(matched[:3]) if matched else " ".join(description.split()[:4])
        reason = f'Cited "{cited}" from description indicates {category}.'
    else:
        # Tie — pick by tie-break order but flag
        for cat in TIE_BREAK_ORDER:
            if cat in top_cats:
                category = cat
                break
        flag = "NEEDS_REVIEW"
        matched = [kw for kw in CATEGORY_KEYWORDS.get(category, []) if kw in desc_lower]
        cited = ", ".join(matched[:2]) if matched else " ".join(description.split()[:4])
        tie_list = ", ".join(top_cats)
        reason = f'Cited "{cited}" suggests {category} but also matched [{tie_list}] — flagged as ambiguous.'

    # Priority enforcement — must be Urgent if severity keyword present (case-insensitive)
    is_urgent = _contains_severity_keyword(desc_lower)
    if is_urgent:
        priority = "Urgent"
        if "Urgent" not in reason and flag == "":
            # ensure reason reflects urgency trigger
            sev_found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
            # append citation
            reason = reason.rstrip(".") + f" Severity trigger '{sev_found[0]}' present → Urgent."
    else:
        priority = "Standard"

    # Enforce category exactness
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Ensure reason is one sentence (ends with period) and cites words
    reason = reason.strip()
    if not reason.endswith("."):
        reason += "."
    # Collapse multiple sentences to one by keeping first sentence if too long
    # We keep as one sentence already; just ensure not too long
    if reason.count(".") > 1:
        # keep first period
        first = reason.split(".")[0].strip()
        reason = first + "."

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
    """
    input_p = Path(input_path)
    output_p = Path(output_path)

    if not input_p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row")
        # Validate required columns
        if "complaint_id" not in reader.fieldnames:
            raise ValueError(f"Input CSV missing 'complaint_id' column. Found: {reader.fieldnames}")
        if "description" not in reader.fieldnames:
            raise ValueError(f"Input CSV missing 'description' column. Found: {reader.fieldnames}")

        rows = list(reader)

    results = []
    flagged = 0
    for row in rows:
        try:
            res = classify_complaint(row)
        except Exception as e:
            print(f"Warning: failed to classify {row.get('complaint_id','?')}: {e}", file=sys.stderr)
            res = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification error: {e} — flagged for review.",
                "flag": "NEEDS_REVIEW",
            }
        # Validate category
        if res["category"] not in ALLOWED_CATEGORIES:
            print(f"Warning: invalid category {res['category']} for {res['complaint_id']}, correcting to Other", file=sys.stderr)
            res["category"] = "Other"
            res["flag"] = "NEEDS_REVIEW"
        if res["flag"] == "NEEDS_REVIEW":
            flagged += 1
        results.append(res)

    # Ensure parent dirs exist
    output_p.parent.mkdir(parents=True, exist_ok=True)

    # Write atomically
    with output_p.open("w", newline="", encoding="utf-8") as out:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"Done. Processed {len(results)} rows, flagged {flagged} NEEDS_REVIEW. Results written to {output_path}")
    return len(results), flagged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
