"""
UC-0A — Complaint Classifier
Deterministic, rule-based implementation guided by agents.md + skills.md.

Enforcement (see agents.md):
  - category: exact strings from the allowed list only
  - priority: Urgent if any severity keyword present
  - reason: one sentence citing words from the description
  - flag: NEEDS_REVIEW when category cannot be determined
  - never crash on bad/empty rows; always produce output
"""
import argparse
import csv
import re

# --- Schema (must match README exactly) -------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Low-priority cues: complaints that are informational, cosmetic, or a minor
# nuisance with no safety dimension. Applied ONLY when no severity keyword is
# present. Severity always wins over these.
LOW_KEYWORDS = [
    "smell", "litter", "cosmetic", "minor", "faded", "peeling",
    "overgrown", "weeds", "graffiti", "untidy", "unkempt",
    "old poster", "stagnant smell", "bad odour", "bad odor",
]

# Category keyword rules. Order matters: the first category whose keywords
# match wins. More specific categories are listed before broader ones so that,
# e.g., "drain blocked" maps to Drain Blockage rather than Flooding, and a
# heritage streetlight maps to Heritage Damage's keyword set deliberately last
# among location-specific checks.
CATEGORY_RULES = [
    ("Drain Blockage", ["drain block", "blocked drain", "drain blocked",
                        "drain 100% blocked", "stormwater drain",
                        "sewer block", "manhole"]),
    ("Heritage Damage", ["heritage", "monument", "historic"]),
    ("Pothole",     ["pothole", "pot hole"]),
    ("Flooding",    ["flood", "waterlog", "water-log", "knee-deep",
                     "knee deep", "stranded in water", "standing in water",
                     "submerged"]),
    ("Streetlight", ["streetlight", "street light", "lights out",
                     "light out", "lamp", "dark at night", "flickering",
                     "unlit", "darkness"]),
    ("Heat Hazard", ["heat", "heatwave", "heat wave", "sunstroke",
                     "no shade", "scorching", "full sun", "dangerous temperature",
                     "high temperature", "exposed to sun"]),
    ("Waste",       ["garbage", "waste", "trash", "dump", "rubbish",
                     "dead animal", "overflowing bin", "litter", "smell"]),
    ("Noise",       ["noise", "loud", "music", "blaring", "honk", "speaker",
                     "band playing", "drilling"]),
    ("Road Damage", ["road", "footpath", "pavement", "crack", "sinking",
                     "broken tiles", "surface", "bridge approach", "paving"]),
]


def _first_match(text: str, keywords: list) -> str:
    """Return the first keyword found in text, or '' if none."""
    for kw in keywords:
        if kw in text:
            return kw
    return ""


def _severity_hit(text: str) -> str:
    """Return the first severity keyword present (word-boundary), else ''."""
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return kw
    return ""


def _low_hit(text: str) -> str:
    """Return the first low-priority cue present, or '' if none."""
    return _first_match(text, LOW_KEYWORDS)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    cid = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Error handling: missing/empty description -> Other + NEEDS_REVIEW.
    if not description:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was missing or empty, so category could not be determined.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # --- Category --------------------------------------------------------
    category = ""
    matched_kw = ""
    for cat, keywords in CATEGORY_RULES:
        hit = _first_match(text, keywords)
        if hit:
            category = cat
            matched_kw = hit
            break

    flag = ""
    if not category:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # --- Priority --------------------------------------------------------
    # Severity always wins. Then a Low cue. Otherwise Standard.
    sev = _severity_hit(text)
    low = "" if sev else _low_hit(text)
    if sev:
        priority = "Urgent"
    elif low:
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason (one sentence, cites specific words) ---------------------
    if sev and matched_kw:
        reason = (f"Classified as {category} from \"{matched_kw}\" and marked "
                  f"Urgent due to severity keyword \"{sev}\".")
    elif sev:
        reason = (f"Category unclear but marked Urgent due to severity keyword "
                  f"\"{sev}\".")
    elif low and matched_kw:
        reason = (f"Classified as {category} from \"{matched_kw}\"; marked Low "
                  f"as a minor issue indicated by \"{low}\".")
    elif matched_kw:
        reason = f"Classified as {category} from the word \"{matched_kw}\"."
    else:
        reason = ("No category keyword matched the description; flagged for "
                  "manual review.")

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Always produces output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # never let one bad row stop the batch
            results.append({
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row could not be classified due to an error: {exc}.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
