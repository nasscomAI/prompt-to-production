"""
UC-0A — Complaint Classifier
Rule-based classifier enforced by uc-0a/agents.md.
The exact allowed taxonomy, severity rules, one-sentence reason and
NEEDS_REVIEW ambiguity handling are implemented as documented in
uc-0a/README.md.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST trigger priority Urgent.
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category -> description keywords (lowercase substring match).
CATEGORY_SIGNALS = [
    ("Pothole",        ["pothole"]),
    ("Drain Blockage", []),
    ("Flooding",       ["flood", "rainwater", "draining"]),
    ("Heat Hazard",    ["melting", "temperature", "bubbling", "storing heat",
                        "unbearable", "sun", "\u00b0c"]),
    ("Streetlight",    ["streetlight", "lights out", "unlit", "darkness",
                        "lamp post", "lamppost", "substation"]),
    ("Waste",          ["garbage", "waste", "bins", "overflow", "dead animal",
                        "not cleared", "not removed", "rubbish", "dump"]),
    ("Noise",          ["music", "amplifier", "drilling", "band", "idling", "loud"]),
    ("Road Damage",    ["cracked", "sinking", "subsided", "subsidence",
                        "collapsed", "buckled", "footpath", "manhole",
                        "crater", "road surface"]),
    ("Heritage Damage", ["heritage", "historic", "ancient", "cobblestones", "tram road"]),
]

# First matching category in this order wins when several signals are present.
CATEGORY_PRECEDENCE = [
    "Pothole", "Drain Blockage", "Flooding", "Heat Hazard", "Streetlight",
    "Waste", "Noise", "Road Damage", "Heritage Damage", "Other",
]


def _detect_ambiguity(desc_lower):
    """Return (cat_a, cat_b, word_a, word_b) when the category is genuinely
    ambiguous, else None. Ambiguity is detected only for explicit conflict
    pairs — never guessed."""
    flood_actual = any(w in desc_lower for w in ("flooded", "floods"))
    drain_blocked = ("drain" in desc_lower) and any(
        w in desc_lower for w in ("blocked", "blocking"))
    if flood_actual and drain_blocked:
        return ("Flooding", "Drain Blockage", "flooded", "drain blocked")

    heritage = any(w in desc_lower for w in
                   ("heritage", "historic", "ancient", "cobblestones", "tram road"))
    if heritage and any(w in desc_lower for w in ("lights out", "lamp post", "lamppost")):
        return ("Heritage Damage", "Streetlight", "heritage", "lights out")
    if heritage and any(w in desc_lower for w in ("subsidence", "subsided")):
        return ("Heritage Damage", "Road Damage", "heritage", "subsidence")
    return None


def _urgent_evidence(desc_lower):
    return [kw for kw in URGENT_KEYWORDS if kw in desc_lower]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    text = str(row.get("description") or "").strip()
    desc_lower = text.lower()
    complaint_id = str(row.get("complaint_id") or "").strip()

    if not desc_lower:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; category cannot be determined and is flagged NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
        }

    ambiguous = _detect_ambiguity(desc_lower)
    if ambiguous:
        cat_a, cat_b, word_a, word_b = ambiguous
        reason = (
            'Genuinely ambiguous between "%s" and "%s": description contains '
            '"%s" and "%s"; category set to Other; flagged NEEDS_REVIEW'
            % (cat_a, cat_b, word_a, word_b)
        )
        urgent = _urgent_evidence(desc_lower)
        if urgent:
            reason += '; priority "Urgent" cited from "%s"' % '", "'.join(urgent)
        else:
            reason += '; priority "Standard"'
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if urgent else "Standard",
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    signals = {}
    for cat, keywords in CATEGORY_SIGNALS:
        for kw in keywords:
            if kw == "sun":
                if re.search(r"\bsun\b", desc_lower):
                    signals.setdefault(cat, "sun")
            elif kw == "band":
                if re.search(r"\bband\b", desc_lower):
                    signals.setdefault(cat, "band")
            elif kw in desc_lower:
                signals.setdefault(cat, kw)
    if ("drain" in desc_lower) and any(
            w in desc_lower for w in ("blocked", "blocking")):
        signals.setdefault("Drain Blockage", "drain blocked")

    category = "Other"
    for cat in CATEGORY_PRECEDENCE:
        if cat in signals:
            category = cat
            break

    urgent = _urgent_evidence(desc_lower)
    priority = "Urgent" if urgent else "Standard"

    if category == "Other":
        reason = 'Category "Other": no allowed category matched the description; priority "%s"' % priority
    else:
        reason = 'Category "%s" cited from "%s"' % (category, signals[category])
        if urgent:
            reason += '; priority "Urgent" cited from "%s"' % '", "'.join(urgent)
        else:
            reason += '; priority "Standard"'

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, and still produces output
    even if some rows fail.
    """
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        missing = [col for col in ("complaint_id", "description") if col not in fieldnames]
        if missing:
            raise ValueError(
                "Input CSV is missing required column(s): %s" % ", ".join(missing))
        rows = list(reader)

    out_rows = []
    skipped = 0
    for index, row in enumerate(rows):
        try:
            out_row = dict(row)
            out_row.update(classify_complaint(row))
            out_rows.append(out_row)
        except Exception as exc:  # never crash the batch on one bad row
            skipped += 1
            print("WARNING: row %d skipped: %s" % (index, exc))

    out_fields = fieldnames + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    flagged = sum(1 for r in out_rows if r.get("flag") == "NEEDS_REVIEW")
    urgent = sum(1 for r in out_rows if r.get("priority") == "Urgent")
    print("Classified %d rows (%d skipped)." % (len(out_rows), skipped))
    print("Urgent: %d | NEEDS_REVIEW: %d" % (urgent, flagged))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)
