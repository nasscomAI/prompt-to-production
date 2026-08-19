"""
UC-0A — Complaint Classifier

Deterministic triage of citizen complaints, built from agents.md + skills.md.

Rules enforced (see agents.md):
  * category  -> exactly one of the ten allowed strings, no variations
  * priority  -> Urgent whenever a severity keyword appears, else keyword-free
                 categories fall back to Standard / Low
  * reason    -> one sentence, cites specific words from the description
  * flag      -> NEEDS_REVIEW only when the category is genuinely ambiguous
The run never crashes on a bad row and always writes a complete output file.
"""
import argparse
import csv
import re

# --- Schema: the only category strings that may ever be emitted ---------------
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# --- Severity keywords that force priority = Urgent ---------------------------
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# --- Category signals: ordered, most-specific first ---------------------------
# Each entry: (category, [keywords]). First category with a matched keyword wins,
# but we also track *how many distinct categories* matched to detect ambiguity.
CATEGORY_SIGNALS = [
    ("Drain Blockage", ["drain block", "drain blocked", "blocked drain", "manhole", "sewer"]),
    # Pothole precedes Flooding: an explicit "pothole" is a more specific signal
    # than a generic water word (e.g. "pothole filling with rainwater").
    ("Pothole",        ["pothole", "pot hole"]),
    ("Flooding",       ["flood", "flooded", "knee-deep", "waterlog", "water logging", "standing in water", "inundat", "rainwater"]),
    ("Streetlight",    ["streetlight", "street light", "lights out", "light out", "lamp", "dark at night", "darkness", "substation tripped", "unlit"]),
    ("Heritage Damage",["heritage", "monument", "old city", "historic"]),
    ("Heat Hazard",    ["heat", "heatstroke", "heat wave", "heatwave", "shade", "temperature", "melting", "°c", "full sun", "exposed to sun"]),
    ("Road Damage",    ["cracked", "sinking", "sunk", "subsid", "footpath", "pavement", "road surface", "tiles broken", "upturned", "bridge", "crater", "buckled", "road collapsed", "tarmac"]),
    ("Waste",          ["garbage", "waste", "dumped", "dump", "trash", "dead animal", "bins", "rubbish", "debris"]),
    ("Noise",          ["music", "noise", "loud", "loudspeaker", "dj", "past midnight", "band playing", "wedding band", "amplifier", "amplifiers", "drilling", "idling", "engines on"]),
]


def _find_severity(text: str):
    """Return the list of severity keywords present in text (case-insensitive)."""
    hits = []
    for kw in SEVERITY_KEYWORDS:
        # word-ish boundary so 'fell' does not match 'fellow'
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            hits.append(kw)
    return hits


def _match_categories(text: str):
    """Return list of (category, matched_keyword) for every category that fires."""
    matches = []
    for category, keywords in CATEGORY_SIGNALS:
        for kw in keywords:
            if kw in text:
                matches.append((category, kw))
                break  # one hit per category is enough
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys complaint_id, category, priority, reason, flag.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Guard: empty / missing description -> Other, NEEDS_REVIEW (skills.md rule)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was empty or missing, so no category could be justified.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # --- Category ------------------------------------------------------------
    matches = _match_categories(text)
    distinct = list(dict.fromkeys(c for c, _ in matches))  # preserve order, dedupe

    flag = ""
    if len(distinct) == 0:
        category = "Other"
        matched_kw = None
        flag = "NEEDS_REVIEW"
    elif len(distinct) == 1:
        category = distinct[0]
        matched_kw = next(kw for c, kw in matches if c == category)
    else:
        # More than one category genuinely supported -> ambiguous.
        # Take the highest-priority (earliest in CATEGORY_SIGNALS) but flag it.
        category = distinct[0]
        matched_kw = next(kw for c, kw in matches if c == category)
        flag = "NEEDS_REVIEW"

    # --- Priority ------------------------------------------------------------
    severity = _find_severity(text)
    if severity:
        priority = "Urgent"
    elif category == "Other":
        priority = "Standard"
    else:
        # Non-urgent, recognised complaint: Standard by default. A handful of
        # low-impact categories default to Low unless a severity word appeared.
        priority = "Low" if category in ("Noise", "Waste") else "Standard"

    # --- Reason (must cite specific words from the description) ---------------
    reason = _build_reason(category, matched_kw, severity, distinct, description)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(category, matched_kw, severity, distinct, description):
    """Compose a one-sentence justification that quotes the description."""
    if category == "Other" and not matched_kw:
        return (
            'No allowed category matched the wording of "'
            + _snippet(description) + '"; flagged for human review.'
        )

    parts = ['Classified as ' + category + ' from the word "' + matched_kw + '"']
    if severity:
        parts.append('marked Urgent due to severity term "' + severity[0] + '"')
    if len(distinct) > 1:
        others = ", ".join(distinct[1:])
        parts.append("flagged because it also reads as " + others)
    return "; ".join(parts) + "."


def _snippet(text, limit=60):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row; always writes a complete output file.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    processed = 0
    flagged = 0

    with open(input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        if reader.fieldnames is None or "description" not in reader.fieldnames:
            raise ValueError(
                "Input CSV must have a header row including a 'description' column."
            )

        with open(output_path, "w", newline="", encoding="utf-8") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as exc:  # bad row -> flag, do not crash
                    result = {
                        "complaint_id": (row.get("complaint_id") or "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row could not be classified: " + str(exc),
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)
                processed += 1
                if result["flag"] == "NEEDS_REVIEW":
                    flagged += 1

    return {"rows_processed": processed, "rows_flagged": flagged}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    summary = batch_classify(args.input, args.output)
    print(
        "Done. Results written to " + args.output
        + " (" + str(summary["rows_processed"]) + " rows, "
        + str(summary["rows_flagged"]) + " flagged NEEDS_REVIEW)."
    )
