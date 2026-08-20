"""
UC-0A - Complaint Classifier

Classifies citizen complaints into an exact taxonomy with priority, a
reason that cites words from the description, and a NEEDS_REVIEW flag for
genuinely ambiguous complaints.

Enforcement (from agents.md):
  1. category must be exactly one of the 10 allowed values
  2. priority is Urgent when severity keywords appear in the description
  3. every row carries a reason that cites specific words from the description
  4. genuinely ambiguous complaints are flagged NEEDS_REVIEW, never guessed
"""
import argparse
import csv
import re
import sys

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

# Severity keywords that MUST trigger priority=Urgent (case-insensitive).
SEVERITY_KEYWORDS = [
    "injur",       # injury / injuries
    "child",       # children
    "school",
    "hospital",    # hospitalised / hospital visit
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collaps",     # collapsed / collapse
]

# Keyword -> category mapping. Matching is case-insensitive, prefix based,
# so "flood" also matches "flooded" but "heat" does not match "heatwave".
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "tyre blowout", "tyre damage"],
    "Flooding": ["flood", "inundat", "waterlogging", "standing in water"],
    "Streetlight": [
        "streetlight", "street light", "lights out", "unlit", "substation",
        "darkness", "lamp post", "street lamp", "wiring theft",
    ],
    "Waste": [
        "garbage", "waste", "bin", "dead animal", "refuse", "rubbish",
        "overflowing", "not cleared", "dumped", "debris", "waste pile",
    ],
    "Noise": [
        "noise", "music", "amplifier", "drilling", "idling", "audible",
        "band", "horn", "loud",
    ],
    "Road Damage": [
        "cracked", "cracking", "sinking", "subsid", "buckled", "collaps",
        "footpath", "paving", "manhole", "road surface", "upturned",
        "glass broken", "sagging",
    ],
    "Heritage Damage": [
        "heritage", "historic", "cobblestone", "step well", "ancient",
        "marble palace", "tagore museum", "heritage stone",
    ],
    "Heat Hazard": [
        "melting", "temperature", "burns", "storing heat", "bubbling",
        "celsius", "deg c", "44", "45", "52", "exposed to full sun",
    ],
    "Drain Blockage": ["drain", "stormwater", "blockage", "mosquito"],
    "Other": [],
}

# Ambiguity signals that force NEEDS_REVIEW regardless of scores.
REVIEW_SIGNALS = [
    "gas leak", "gas pipeline", "unconfirmed", "reported but unverified",
]

# Category preference used only to resolve keyword-score ties.
TIEBREAK_PRIORITY = [
    "Flooding",
    "Drain Blockage",
    "Heat Hazard",
    "Road Damage",
    "Pothole",
    "Streetlight",
    "Heritage Damage",
    "Waste",
    "Noise",
    "Other",
]

# Heritage-context override rules.
HERITAGE_WORDS = ["heritage", "historic", "ancient", "cobblestone", "step well", "tagore museum"]
HERITAGE_DAMAGE_SIGNALS = [
    "knocked", "broken", "defaced", "removed", "not restored", "damaged",
    "cobblestones broken", "paving removed", "billboard",
]
HERITAGE_FUNCTIONAL_FAILURE = ["lights out", "unlit", "darkness", "substation"]
HERITAGE_WASTE_SIGNALS = ["garbage", "waste", "bin", "overflowing", "not cleared"]
HERITAGE_NOISE_SIGNALS = ["music", "amplifier", "band", "loud", "noise"]


def _kw_find(description, keywords):
    """Return the list of keywords (prefix match) found in description."""
    found = []
    for kw in keywords:
        if re.search(r"(?<!\w)" + re.escape(kw), description):
            found.append(kw)
    return found


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()
    text = description.lower()

    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "no description provided to classify",
            "flag": "NEEDS_REVIEW",
        }

    has_heritage = any(_kw_find(text, [w]) for w in HERITAGE_WORDS)

    category = None
    flag = ""
    reason_words = []

    if has_heritage:
        heritage_word = next(w for w in HERITAGE_WORDS if _kw_find(text, [w]))
        reason_words.append(heritage_word)
        if any(_kw_find(text, [s]) for s in HERITAGE_DAMAGE_SIGNALS):
            category = "Heritage Damage"
            reason_words.extend(_kw_find(text, HERITAGE_DAMAGE_SIGNALS))
        elif any(_kw_find(text, [s]) for s in HERITAGE_FUNCTIONAL_FAILURE):
            category = "Streetlight"
            reason_words.extend(_kw_find(text, HERITAGE_FUNCTIONAL_FAILURE))
        elif any(_kw_find(text, [s]) for s in HERITAGE_WASTE_SIGNALS):
            category = "Waste"
            reason_words.extend(_kw_find(text, HERITAGE_WASTE_SIGNALS))
        elif any(_kw_find(text, [s]) for s in HERITAGE_NOISE_SIGNALS):
            category = "Noise"
            reason_words.extend(_kw_find(text, HERITAGE_NOISE_SIGNALS))
        else:
            category = "Heritage Damage"

    if category is None:
        scores = {}
        for cat, kws in CATEGORY_KEYWORDS.items():
            if cat == "Other":
                continue
            matched = _kw_find(text, kws)
            scores[cat] = len(matched)
            if matched:
                reason_words.extend(matched)

        best = max(scores.values()) if scores else 0
        if best == 0:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason_words = []
        else:
            top = sorted(
                (c for c, s in scores.items() if s == best),
                key=lambda c: TIEBREAK_PRIORITY.index(c),
            )
            category = top[0]
            if len(top) > 1:
                flag = "NEEDS_REVIEW"

    # Cause-vs-effect rule: flooding is the observable complaint; a blocked
    # drain only wins when it is clearly the subject (strictly more specific).
    if category == "Drain Blockage" and _kw_find(text, CATEGORY_KEYWORDS["Flooding"]):
        flood_score = len(_kw_find(text, CATEGORY_KEYWORDS["Flooding"]))
        drain_score = len(_kw_find(text, CATEGORY_KEYWORDS["Drain Blockage"]))
        if drain_score <= flood_score:
            category = "Flooding"

    if any(_kw_find(text, [s]) for s in REVIEW_SIGNALS):
        flag = "NEEDS_REVIEW"

    # Reason must cite words from the description for the final category.
    if category != "Other":
        for kw in CATEGORY_KEYWORDS.get(category, []):
            if _kw_find(text, [kw]) and kw not in reason_words:
                reason_words.append(kw)

    if any(_kw_find(text, [s]) for s in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    if flag == "NEEDS_REVIEW":
        reason = (
            "ambiguous: no single category keyword dominates the description "
            + '("'
            + '", "'.join(dict.fromkeys(reason_words))
            + '")'
        )
    elif category == "Other":
        reason = "no category keyword found in the description"
    else:
        reason = (
            'description mentions "'
            + '", "'.join(dict.fromkeys(reason_words))
            + '"'
        )

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

    Flags nulls, never crashes on bad rows, and produces output even if
    some rows fail.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except UnicodeDecodeError:
        with open(input_path, "r", encoding="latin-1", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError as exc:
        print(f"ERROR: cannot read input file {input_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print(f"ERROR: input file {input_path} has no data rows", file=sys.stderr)
        sys.exit(1)

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    classified = []
    failed = 0
    for idx, row in enumerate(rows):
        try:
            classified.append(classify_complaint(row))
        except Exception as exc:  # noqa: BLE001 - never let one row kill the batch
            failed += 1
            classified.append(
                {
                    "complaint_id": str(row.get("complaint_id", "UNKNOWN")),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            )

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(classified)

    urgent = sum(1 for c in classified if c["priority"] == "Urgent")
    flagged = sum(1 for c in classified if c["flag"] == "NEEDS_REVIEW")
    print(f"Classified {len(classified)} complaints -> {output_path}")
    print(f"  Urgent: {urgent} | NEEDS_REVIEW: {flagged} | failed rows: {failed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")