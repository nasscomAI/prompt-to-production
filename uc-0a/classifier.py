"""
UC-0A — Complaint Classifier

Deterministic, keyword-driven implementation of the classification schema in
README.md, honoring the enforcement rules in agents.md and the skill contracts
in skills.md.

Each complaint is classified from its own description alone, so outputs are
reproducible and machine-checkable against the closed category/priority
vocabularies. No row's result depends on any other row.
"""
import argparse
import csv
import re

# --- Closed vocabularies (agents.md enforcement rules 1 & 2) ------------------

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that FORCE priority = Urgent. Matched on word boundaries so
# "fell" does not fire inside "fellow", etc. (agents.md enforcement rule 2).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category signal keywords. Matched as case-insensitive substrings so plurals
# and compounds count ("potholes" -> "pothole", "streetlights" -> "streetlight").
# Address words like a bare "road" are deliberately excluded to avoid matching
# every street name; only damage-specific phrases score for Road Damage.
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole"],
    "Flooding":        ["flood", "knee-deep", "stranded", "waterlogged", "inundated",
                        "standing in water"],
    "Streetlight":     ["streetlight", "street light", "flickering", "lamp",
                        "lights out", "light out", "unlit", "darkness"],
    "Waste":           ["garbage", "waste", "trash", "dump", "bins", "litter",
                        "dead animal", "smell"],
    "Noise":           ["noise", "music", "loudspeaker", "loud", "drilling",
                        "wedding band", "brass band"],
    "Road Damage":     ["road surface", "cracked", "sinking", "footpath",
                        "tiles broken", "subsidence", "road damage", "manhole",
                        "paving", "crater"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    # Heat in this data is expressed as temperature/melting/sun, not the word
    # "heat" — these synonyms recover the Heat Hazard complaints.
    "Heat Hazard":     ["heat", "heatwave", "heat wave", "scorching", "temperature",
                        "melting", "unbearable", "full sun", "°c"],
    "Drain Blockage":  ["drain", "drainage", "sewer", "sewage"],
}

# Category pairs that naturally co-occur as cause/effect. When the top score
# ties between exactly these two, resolve to the lead signal (whichever is
# mentioned first) instead of flagging — the tie is structural, not genuine
# ambiguity. All other ties remain NEEDS_REVIEW.
RELATED_PAIRS = {frozenset({"Flooding", "Drain Blockage"})}


def _matched_severity(text: str) -> list:
    """Return severity keywords present in text (word-boundary matched)."""
    return [kw for kw in SEVERITY_KEYWORDS
            if re.search(r"\b" + re.escape(kw) + r"\b", text)]


def _category_scores(text: str) -> dict:
    """Map each category to the list of its keywords found in text."""
    return {
        cat: [kw for kw in kws if kw in text]
        for cat, kws in CATEGORY_KEYWORDS.items()
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row (skills.md: classify_complaint).

    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    Honors the agents.md enforcement rules: closed category/priority sets,
    severity keywords force Urgent, a citing reason is always present, and
    genuine ambiguity yields category "Other" + flag "NEEDS_REVIEW".
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Missing/empty description -> cannot classify, flag for review.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty, so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    severity_hits = _matched_severity(text)
    scores = {cat: hits for cat, hits in _category_scores(text).items() if hits}

    best = max((len(h) for h in scores.values()), default=0)
    top = [cat for cat, hits in scores.items() if len(hits) == best]

    # Decide category + flag.
    if best == 0:
        category, flag = "Other", "NEEDS_REVIEW"
        reason = "No recognizable category keyword found in the description."
    elif len(top) > 1 and frozenset(top) in RELATED_PAIRS:
        # Structural cause/effect pair: resolve to the lead (first-mentioned).
        category = min(top, key=lambda c: min(text.find(kw) for kw in scores[c]))
        flag = ""
        cited = ", ".join(f'"{w}"' for w in scores[category])
        reason = (f"Description cites {cited}; resolved to lead signal "
                  f"{category} over related {'/'.join(t for t in top if t != category)}.")
    elif len(top) > 1:
        # Two or more categories tie -> genuinely ambiguous.
        category, flag = "Other", "NEEDS_REVIEW"
        cited = ", ".join(f'"{scores[c][0]}"' for c in top)
        reason = (f"Description fits {' and '.join(top)} equally "
                  f"(cites {cited}); ambiguous, flagged for review.")
    else:
        category, flag = top[0], ""
        cited = ", ".join(f'"{w}"' for w in scores[category])
        reason = f"Description cites {cited}, indicating {category}."

    # Decide priority. Severity keywords always win (enforcement rule 2).
    if severity_hits:
        priority = "Urgent"
        reason += f' Severity term "{severity_hits[0]}" forces Urgent.'
    elif category == "Noise":
        # Pure nuisance with no safety signal: lowest triage tier.
        priority = "Low"
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV (skills.md:
    batch_classify).

    Never crashes on a malformed row: per-row failures are caught and emitted
    as Other/Standard/NEEDS_REVIEW so an output file is always produced.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    total = failed = 0

    with open(input_path, newline="", encoding="utf-8") as fin, \
            open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1
            try:
                writer.writerow(classify_complaint(row))
            except Exception as exc:  # never let one bad row abort the batch
                failed += 1
                writer.writerow({
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be classified: {exc}.",
                    "flag": "NEEDS_REVIEW",
                })

    print(f"Classified {total} rows ({failed} failed) -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
