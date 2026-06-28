"""
UC-0A — Complaint Classifier

Rule-based municipal complaint classifier built from the RICE enforcement rules
in agents.md. Deterministic and offline (no LLM call) so every classification is
defensible by the exact keywords it matched in the complaint description.

Guards against the documented failure modes:
  - Taxonomy drift        -> category is always one of CATEGORIES (exact strings)
  - Severity blindness     -> SEVERITY_KEYWORDS force priority = Urgent
  - Missing justification  -> reason always cites the words that drove the decision
  - Hallucinated subtypes   -> only the fixed 10-category taxonomy is ever emitted
  - False confidence        -> ties across categories => flag NEEDS_REVIEW
"""
import argparse
import csv

# --- Taxonomy (exact strings — no variations allowed) ------------------------
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Ordered keyword signals per category. Match is case-insensitive substring.
CATEGORY_KEYWORDS = {
    "Pothole":        ["pothole"],
    "Flooding":       ["flood", "knee-deep", "waterlog", "standing in water",
                       "inundat", "submerged"],
    "Drain Blockage": ["drain block", "blocked drain", "drain blocked",
                       "manhole", "sewage", "sewer", "clogged drain"],
    "Streetlight":    ["streetlight", "street light", "lights out", "light out",
                       "flickering", "lamp post", "lamppost", "dark at night"],
    "Waste":          ["garbage", "waste", "trash", "dump", "dead animal",
                       "litter", "rubbish", "overflowing bin"],
    "Noise":          ["music", "noise", "loud", "loudspeaker", "blaring"],
    "Road Damage":    ["road surface", "cracked", "sinking", "footpath",
                       "tiles broken", "road damage", "sinkhole", "caved in"],
    "Heritage Damage": ["heritage", "monument", "historic", "fort wall"],
    "Heat Hazard":    ["heatwave", "heat hazard", "extreme heat", "heat stroke"],
}

# Severity keywords from the README — any of these forces Urgent.
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance",
                     "fire", "hazard", "fell", "collapse"]

REQUIRED_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _score_categories(text: str):
    """Return {category: [matched keywords]} for every category that matched."""
    hits = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in text]
        if matched:
            hits[category] = matched
    return hits


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag.
    Never raises — a malformed row is returned flagged for review.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify from available text.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    hits = _score_categories(text)

    # --- Category decision ---------------------------------------------------
    flag = ""
    if not hits:
        category = "Other"
        category_words = []
        flag = "NEEDS_REVIEW"  # no taxonomy signal -> do not fake confidence
    else:
        # Rank by number of distinct keyword matches.
        ranked = sorted(hits.items(), key=lambda kv: len(kv[1]), reverse=True)
        top_score = len(ranked[0][1])
        leaders = [cat for cat, kws in ranked if len(kws) == top_score]
        category = ranked[0][0]
        category_words = hits[category]
        if len(leaders) > 1:
            # Genuine ambiguity: 2+ categories tie. Keep best guess, flag it.
            flag = "NEEDS_REVIEW"

    # --- Priority decision ---------------------------------------------------
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    priority = "Urgent" if severity_hits else "Standard"

    # --- Reason (always cites the words that drove the decision) -------------
    if category_words:
        reason = f"Classified as {category} — description cites " \
                 f"{', '.join(repr(w) for w in category_words[:3])}"
    else:
        reason = "No clear category keyword found in description"
    if severity_hits:
        reason += f"; marked Urgent due to severity term(s) " \
                  f"{', '.join(repr(w) for w in severity_hits[:3])}"
    if flag and len(hits) > 1:
        others = [c for c in hits if c != category]
        reason += f"; ambiguous with {', '.join(others)}"
    reason += "."

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
    Tolerates malformed rows (flags them) and always produces output.
    Output = original columns + category, priority, reason, flag.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        base_fields = reader.fieldnames or []

    out_fields = list(base_fields)
    for extra in ("category", "priority", "reason", "flag"):
        if extra not in out_fields:
            out_fields.append(extra)

    processed, flagged = 0, 0
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never crash the batch on one bad row
                result = {
                    "category": "Other", "priority": "Standard",
                    "reason": f"Row could not be processed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            out_row = dict(row)
            out_row.update({k: result[k] for k in
                            ("category", "priority", "reason", "flag")})
            writer.writerow(out_row)
            processed += 1
            if result["flag"]:
                flagged += 1

    print(f"Processed {processed} rows ({flagged} flagged NEEDS_REVIEW).")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
