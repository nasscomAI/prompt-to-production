"""
UC-0A — Complaint Classifier
Civic complaint triage with RICE enforcement encoded directly in code.

The enforcement rules from agents.md are not advisory here — they are the
control flow. Category is constrained to a fixed taxonomy, severity keywords
deterministically force Urgent priority, every row carries a reason citing the
words that drove the decision, and genuine ambiguity is flagged for review
rather than guessed.
"""
import argparse
import csv

# --- Enforcement constant: the ONLY categories allowed to ever appear. ---
# Taxonomy drift is prevented by construction: classify_complaint can only
# emit a string from this list (or "Other").
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST escalate a complaint to Urgent (README schema).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered category -> trigger keywords. Order matters only for the tie-break
# audit trail; scoring below is what actually selects the category.
CATEGORY_KEYWORDS = {
    "Heritage Damage": ["heritage"],
    "Drain Blockage": ["drain blocked", "drain block", "blocked drain", "drain"],
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "knee-deep", "waterlogg", "inundat", "stranded"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out",
                    "lights are out", "lamp", "flickering"],
    "Waste": ["garbage", "waste", "trash", "bins", "bin ", "dumped",
              "dumping", "dead animal", "rubbish", "litter"],
    "Noise": ["music", "noise", "loud", "loudspeaker"],
    "Road Damage": ["road surface", "cracked", "sinking", "manhole",
                    "footpath", "tiles broken", "pavement", "subsidence"],
    "Heat Hazard": ["heat", "heatwave", "heat hazard"],
}

# Categories whose complaints are quality-of-life rather than safety: eligible
# for Low priority when no severity keyword is present.
LOW_IMPACT_CATEGORIES = {"Noise"}


def _find_keywords(text: str, keywords: list) -> list:
    """Return the keywords that appear in text, preserving caller order."""
    return [kw for kw in keywords if kw in text]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement (mirrors agents.md):
      * category is always one of ALLOWED_CATEGORIES — never invented.
      * priority is Urgent iff a severity keyword is present in the description.
      * reason always cites the specific words that drove the decision.
      * flag = NEEDS_REVIEW when the description is missing, no category matches,
        or two categories tie — i.e. when confidence is not warranted.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Null / empty input is flagged, never silently classified.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty or missing; cannot classify from data alone.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Score every category by how many of its keywords are present.
    scores = {}
    matched = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = _find_keywords(text, keywords)
        if hits:
            scores[category] = len(hits)
            matched[category] = hits

    # Severity detection drives priority independently of category.
    severity_hits = _find_keywords(text, SEVERITY_KEYWORDS)

    if not scores:
        # No taxonomy match: refuse to guess. Other + NEEDS_REVIEW.
        priority = "Urgent" if severity_hits else "Standard"
        sev = f" Severity keyword(s) {severity_hits} present." if severity_hits else ""
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": ("No allowed category keyword found in description; "
                       "left as Other for human review." + sev),
            "flag": "NEEDS_REVIEW",
        }

    # Pick the highest-scoring category; detect ambiguity (a real tie).
    top_score = max(scores.values())
    leaders = [c for c, s in scores.items() if s == top_score]
    # Deterministic pick: follow CATEGORY_KEYWORDS declaration order.
    category = next(c for c in CATEGORY_KEYWORDS if c in leaders)

    ambiguous = len(leaders) > 1
    flag = "NEEDS_REVIEW" if ambiguous else ""

    # Priority: severity keyword forces Urgent; else Low for quality-of-life
    # categories, else Standard.
    if severity_hits:
        priority = "Urgent"
    elif category in LOW_IMPACT_CATEGORIES:
        priority = "Low"
    else:
        priority = "Standard"

    # Build a reason that cites the exact words behind the decision.
    reason_parts = [f"Category '{category}' from keyword(s) {matched[category]}"]
    if severity_hits:
        reason_parts.append(f"escalated to Urgent by severity keyword(s) {severity_hits}")
    if ambiguous:
        others = [c for c in leaders if c != category]
        reason_parts.append(f"ambiguous with {others} — flagged for review")
    reason = "; ".join(reason_parts) + "."

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

    Robustness enforcement:
      * a malformed/exception-raising row never aborts the batch — it is
        captured as Other / NEEDS_REVIEW with the error noted in reason.
      * output is always produced, even if some rows failed.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:  # never crash the batch on one bad row
                results.append({
                    "complaint_id": (row.get("complaint_id") or f"ROW_{i}").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be processed: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    print(f"Classified {len(results)} complaints "
          f"({urgent} Urgent, {flagged} flagged NEEDS_REVIEW).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
