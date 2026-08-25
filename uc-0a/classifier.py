"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md (R.I.C.E)
and skills.md specifications.
"""
import argparse
import csv
import sys
import re

# ---------------------------------------------------------------------------
# Enforcement constants (from agents.md)
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ---------------------------------------------------------------------------
# Category keyword map — order matters: first match wins
# Each entry: (category_name, list_of_keyword_patterns)
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "pot-hole"]),
    ("Flooding",        ["flood", "waterlog", "water-log", "submerge", "inundat"]),
    ("Streetlight",     ["streetlight", "street light", "street-light", "lamp post",
                         "light pole", "bulb out", "no light", "broken light",
                         "faulty light", "dark street", "street lamp"]),
    ("Drain Blockage",  ["drain", "sewer", "gutter", "manhole", "clog",
                         "blockage", "blocked drain", "storm water"]),
    ("Waste",           ["garbage", "waste", "trash", "dump", "litter",
                         "rubbish", "refuse", "debris", "sanitation"]),
    ("Noise",           ["noise", "loud", "honk", "disturbance", "blaring",
                         "decibel", "sound pollution", "noise pollution"]),
    ("Road Damage",     ["road damage", "crack in road", "broken road",
                         "road surface", "asphalt", "road cave", "road crack",
                         "damaged road", "road repair", "road break"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient",
                         "archaeological", "heritage site", "old building",
                         "temple damage", "protected structure"]),
    ("Heat Hazard",     ["heat", "heatwave", "heat wave", "sunstroke",
                         "hot surface", "heat stroke", "burning surface",
                         "high temperature", "thermal"]),
]


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : dict with at least 'complaint_id' and 'description'.
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement rules (agents.md):
      - category  ∈ ALLOWED_CATEGORIES (exact string)
      - priority  ∈ {Urgent, Standard, Low}; Urgent when severity keywords present
      - reason    = one sentence citing words from the description
      - flag      = 'NEEDS_REVIEW' when category is ambiguous, else blank
      - complaint_id preserved unchanged
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # --- guard: missing / empty description ---------------------------------
    if not description or not isinstance(description, str):
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- 1. Determine priority (severity-keyword scan) ----------------------
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if matched_severity else "Standard"

    # --- 2. Determine category (first-match keyword scan) -------------------
    category = None
    matched_cat_keywords: list[str] = []

    for cat_name, patterns in CATEGORY_KEYWORDS:
        hits = [p for p in patterns if p in desc_lower]
        if hits:
            category = cat_name
            matched_cat_keywords = hits
            break

    # If no keyword matched, check for pothole-like surface issues
    if category is None:
        # Ambiguous — fall back to Other + flag
        category = "Other"
        flag = "NEEDS_REVIEW"
        cited = _extract_salient_words(description)
        reason = (
            f"Could not confidently determine category from description "
            f"containing: {cited}; flagged for manual review."
        )
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    # --- 3. Build reason sentence -------------------------------------------
    flag = ""
    cat_citation = ", ".join(f"'{w}'" for w in matched_cat_keywords[:3])
    if matched_severity:
        sev_citation = ", ".join(f"'{w}'" for w in matched_severity[:3])
        reason = (
            f"Classified as {category} due to keyword(s) {cat_citation} "
            f"and marked Urgent due to severity keyword(s) {sev_citation} "
            f"found in the description."
        )
    else:
        reason = (
            f"Classified as {category} due to keyword(s) {cat_citation} "
            f"found in the description; no severity keywords detected so "
            f"priority is Standard."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint to every row, write results CSV.

    - Never crashes the batch; failed rows get Other / Low / NEEDS_REVIEW.
    - No rows dropped or duplicated.
    - Warnings for bad rows printed to stderr.
    """

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results: list[dict] = []

    # --- read ---------------------------------------------------------------
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as exc:
        print(f"FATAL: Cannot read input file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # --- classify each row --------------------------------------------------
    for idx, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:
            complaint_id = row.get("complaint_id", f"ROW_{idx}")
            print(
                f"WARNING: Row {idx} (complaint_id={complaint_id}) failed: {exc}",
                file=sys.stderr,
            )
            result = {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed due to error: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    # --- write --------------------------------------------------------------
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        print(f"FATAL: Cannot write output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Classified {len(results)} complaints ({len(rows)} input rows).")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_salient_words(text: str, max_words: int = 5) -> str:
    """Return a short quoted list of significant words from the text."""
    stop = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
            "to", "of", "and", "or", "for", "it", "my", "our", "has", "have",
            "been", "be", "with", "this", "that", "from", "not", "very", "near"}
    words = re.findall(r"[a-zA-Z]+", text.lower())
    salient = [w for w in words if w not in stop and len(w) > 2]
    unique = list(dict.fromkeys(salient))[:max_words]
    return ", ".join(f"'{w}'" for w in unique)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
