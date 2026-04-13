"""
UC-0A — Complaint Classifier

Implements the contract defined in agents.md and skills.md:
  - classify_complaint(row) -> dict
  - batch_classify(input_path, output_path) -> None

Rules enforced (see agents.md):
  * category MUST be one of the ten canonical labels.
  * priority is Urgent if any severity keyword appears in the description.
  * reason is a single sentence citing specific words from the description.
  * Ambiguous / empty descriptions => category="Other", flag="NEEDS_REVIEW".
  * Never crash on a bad row; always emit one output row per input row.
"""
import argparse
import csv
import os
import re
import tempfile

# ---- Fixed taxonomy (agents.md enforcement) --------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword -> canonical category. Order matters: earlier rules win on ties.
CATEGORY_RULES = [
    ("Pothole",         [r"\bpothole[s]?\b", r"\bcrater\b"]),
    ("Flooding",        [r"\bflood(?:ing|ed)?\b", r"\bwater ?logg(?:ed|ing)\b", r"\binundat"]),
    ("Drain Blockage",  [r"\bdrain\b", r"\bsewer\b", r"\bmanhole\b", r"\bclogged\b"]),
    ("Streetlight",     [r"\bstreet ?light\b", r"\blamp ?post\b", r"\bstreet lamp\b"]),
    ("Waste",           [r"\bgarbage\b", r"\btrash\b", r"\brubbish\b", r"\bwaste\b", r"\bdump\b", r"\blitter\b"]),
    ("Noise",           [r"\bnoise\b", r"\bloud\b", r"\bnoisy\b", r"\bloudspeaker\b"]),
    ("Road Damage",     [r"\broad damage\b", r"\bcracked road\b", r"\bbroken road\b", r"\bpavement\b", r"\bfootpath\b"]),
    ("Heritage Damage", [r"\bheritage\b", r"\bmonument\b", r"\bstatue\b", r"\bfort\b", r"\btemple\b"]),
    ("Heat Hazard",     [r"\bheat\b", r"\bheatstroke\b", r"\bheat wave\b", r"\bheatwave\b"]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


# ---- Core skill: classify_complaint ----------------------------------------

def _first_keyword_hit(text: str, keywords):
    lower = text.lower()
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            return kw
    return None


def _match_categories(text: str):
    """Return list of (category, matched_word) tuples for every rule that fires."""
    hits = []
    for category, patterns in CATEGORY_RULES:
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                hits.append((category, m.group(0)))
                break
    return hits


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row. Never raises."""
    complaint_id = str(row.get("complaint_id", "") or "").strip()
    description = (row.get("description") or "").strip()

    # Empty / missing description -> flagged Other.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "description missing or empty; cannot classify",
            "flag": "NEEDS_REVIEW",
        }

    # Severity detection (forces Urgent regardless of category certainty).
    severity_hit = _first_keyword_hit(description, SEVERITY_KEYWORDS)

    # Category detection.
    hits = _match_categories(description)
    distinct_categories = {c for c, _ in hits}

    if len(distinct_categories) == 1:
        category, matched_word = hits[0]
        flag = ""
        cite = f'mentions "{matched_word}"'
    elif len(distinct_categories) > 1:
        # Genuinely ambiguous — multiple canonical categories fit.
        category = "Other"
        flag = "NEEDS_REVIEW"
        cite = "matches multiple categories: " + ", ".join(sorted(distinct_categories))
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cite = "no canonical category keywords found in description"

    # Priority rule (severity keywords dominate).
    if severity_hit:
        priority = "Urgent"
        reason = (
            f'Urgent because description contains severity keyword "{severity_hit}"; '
            f"{cite}."
        )
    else:
        priority = "Low" if re.search(r"\b(minor|cosmetic|small)\b", description, re.IGNORECASE) else "Standard"
        reason = f"{cite[0].upper() + cite[1:]}."

    if category not in ALLOWED_CATEGORIES:  # safety net
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---- Core skill: batch_classify --------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write results CSV atomically."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_dir = os.path.dirname(os.path.abspath(output_path)) or "."
    os.makedirs(out_dir, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(prefix=".classifier_", suffix=".csv", dir=out_dir)
    os.close(fd)
    try:
        with open(tmp_path, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            for i, row in enumerate(rows):
                try:
                    result = classify_complaint(row)
                except Exception as e:  # never abort mid-file
                    result = {
                        "complaint_id": str(row.get("complaint_id", "") or "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"row {i} failed during classification: {e!r}",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)
        os.replace(tmp_path, output_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# ---- CLI -------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
