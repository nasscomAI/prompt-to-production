"""
UC-0A — Complaint Classifier
Deterministic, rules-based classifier built via the RICE → agents.md →
skills.md → CRAFT workflow. See README.md for schema and run command.

Enforcement (mirrors agents.md):
  1. category is EXACTLY one of the allowed taxonomy strings.
  2. priority is Urgent whenever a severity keyword appears in the description.
  3. Every output row carries a reason citing specific words from the description.
  4. Genuinely ambiguous rows get flag=NEEDS_REVIEW and are never guessed confidently.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered most-specific first. Each entry: (category, [regex patterns]).
# Scoring: each DISTINCT matched pattern scores 2 if multi-word, else 1;
# ties resolve by earliest first occurrence in the description, then rule order.
CATEGORY_RULES = [
    ("Heritage Damage", [r"heritage", r"historic"]),
    ("Flooding", [r"flood", r"water\s*logging", r"inundat", r"standing water", r"rainwater"]),
    ("Drain Blockage", [r"drain\w*\s+(?:is\s+|completely\s+|partially\s+|100%\s+)?blocked",
                        r"blocked\s+drain", r"drain\s+blockage", r"clogged", r"draining\b"]),
    ("Pothole", [r"potholes?", r"pot\s+holes?"]),
    ("Road Damage", [r"road\s+surface", r"manhole", r"footpath", r"tiles?\s+broken", r"upturned",
                     r"\bsinking\b", r"\bsubsid\w*\b", r"cracked", r"crumbling",
                     r"road\s+damage", r"buckled", r"cobblestones?", r"paving", r"crater",
                     r"\bcollapsed?\b"]),
    ("Streetlight", [r"street\s?lights?", r"streetlights?", r"lights?\s+out", r"lamp\s?posts?",
                     r"flickering", r"sparking", r"\bunlit\b"]),
    ("Waste", [r"garbage", r"\bwaste\b", r"trash", r"litter", r"dumped", r"debris",
               r"dead\s+animal", r"overflowing\s+bins?", r"waste\s+bins?", r"\bbins?\b"]),
    ("Noise", [r"\bnoise\b", r"\bloud\b", r"loudspeaker", r"\bmusic\b", r"amplifier\w*",
               r"band\s+playing", r"drilling"]),
    ("Heat Hazard", [r"heat\s*waves?", r"heatwave", r"extreme\s+heat", r"heat\s+stroke",
                     r"heat\s+hazard", r"\bheat\b", r"melting", r"temperatures?",
                     r"\d+\s*°\s*c", r"\bburns?\b", r"bubbling"]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _find_matches(text_lower, patterns):
    found = []
    for pat in patterns:
        m = re.search(pat, text_lower)
        if m:
            found.append(m.group(0))
    return found


def _pattern_weight(pattern):
    # multi-word pattern (\s or literal space inside) = more specific evidence
    return 2 if ("\\s" in pattern or " " in pattern) else 1


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()
    text = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify from empty text.",
            "flag": "NEEDS_REVIEW",
        }

    # --- Category scoring -------------------------------------------------
    scores = {}      # category -> weighted score of distinct matched patterns
    evidence = {}    # category -> matched words (for the reason field)
    positions = {}   # category -> earliest first-match position
    for category, patterns in CATEGORY_RULES:
        cat_score = 0
        cat_words = []
        cat_pos = None
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                cat_score += _pattern_weight(pat)
                cat_words.append(m.group(0))
                if cat_pos is None or m.start() < cat_pos:
                    cat_pos = m.start()
        if cat_score:
            scores[category] = cat_score
            evidence[category] = cat_words
            positions[category] = cat_pos

    tie = False
    if not scores:
        category = "Other"
        cat_words = []
        flag = "NEEDS_REVIEW"
    else:
        best = max(scores.values())
        top = [c for c, s in scores.items() if s == best]
        if len(top) > 1:
            tie = True
            # resolve: earliest mention wins, then rule order (already ordered)
            top.sort(key=lambda c: positions[c])
        category = top[0]
        cat_words = sorted(set(evidence[category]), key=lambda w: text.find(w))[:3]

    # --- Priority ---------------------------------------------------------
    sev_hits = _find_matches(text, SEVERITY_KEYWORDS)
    sev_hits = sorted(set(sev_hits))
    if sev_hits:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason (must cite specific words from the description) -----------
    parts = []
    if cat_words:
        quoted = ", ".join("'%s'" % w for w in cat_words)
        parts.append("Description mentions %s indicating %s" % (quoted, category.lower()))
    else:
        parts.append("No recognised category keywords in description")
    if sev_hits:
        quoted_sev = ", ".join("'%s'" % w for w in sev_hits[:3])
        parts.append("severity terms %s present so Urgent" % quoted_sev)
    elif priority == "Low":
        parts.append("pure nuisance issue with no severity terms so Low")
    else:
        parts.append("no severity keywords present so Standard")
    reason = "; ".join(parts) + "."

    # --- Flag -------------------------------------------------------------
    flag = ""
    if category == "Other" or tie:
        flag = "NEEDS_REVIEW"

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        f_in = open(input_path, "r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        print("ERROR: cannot read input file '%s': %s" % (input_path, exc))
        sys.exit(1)

    classified = errors = flagged = 0
    rows_out = []
    with f_in as fin:
        reader = csv.DictReader(fin)
        for idx, row in enumerate(reader):
            try:
                result = classify_complaint(row)
                if not (row.get("description") or "").strip():
                    errors += 1
                elif result["flag"] == "NEEDS_REVIEW":
                    flagged += 1
                else:
                    classified += 1
            except Exception as exc:  # never let one bad row kill the batch
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip() or "ROW-%d" % idx,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification failed (%s); routed for manual review." % exc.__class__.__name__,
                    "flag": "NEEDS_REVIEW",
                }
                errors += 1
            rows_out.append(result)

    try:
        f_out = open(output_path, "w", encoding="utf-8", newline="")
    except OSError as exc:
        print("ERROR: cannot write output file '%s': %s" % (output_path, exc))
        sys.exit(1)

    with f_out as fout:
        writer = csv.DictWriter(fout, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows_out)

    print("Classified %d rows (%d clean, %d NEEDS_REVIEW, %d skipped/invalid) -> %s"
          % (len(rows_out), classified, flagged, errors, output_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
