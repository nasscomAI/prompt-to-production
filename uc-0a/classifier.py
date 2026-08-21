"""
UC-0A — Complaint Classifier
Deterministic, rules-based classifier built to satisfy the enforcement
rules in agents.md and the skill contracts in skills.md.

Taxonomy (exact strings only):
    Pothole | Flooding | Streetlight | Waste | Noise | Road Damage |
    Heritage Damage | Heat Hazard | Drain Blockage | Other

Priority:
    Urgent    — description contains any severity keyword
                (injury, child, school, hospital, ambulance, fire,
                 hazard, fell, collapse)
    Standard  — default when no severity keyword is present
    Low       — explicitly minor reports ("minor", "cosmetic",
                "no risk", "not urgent") with no severity keyword

Flag:
    NEEDS_REVIEW — set when the category is genuinely ambiguous
                   (no keyword match at all, or a tie between categories)
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

LOW_PRIORITY_MARKERS = ["minor", "cosmetic", "no risk", "not urgent"]

# Category -> list of (keyword substring, weight).
# Weights: 3 = names the problem, 2 = strong supporting signal,
# 1 = weak supporting signal.
CATEGORY_KEYWORDS = {
    "Pothole": [("pothole", 3)],
    "Flooding": [("flood", 3), ("waterlog", 3), ("standing water", 3)],
    "Streetlight": [
        ("streetlight", 3), ("street light", 3), ("lamp post", 3),
        ("lights out", 3), ("unlit", 3), ("darkness", 2),
        ("flickering", 2), ("sparking", 2),
    ],
    "Waste": [
        ("garbage", 3), ("waste", 3), ("trash", 3), ("litter", 3),
        ("dead animal", 3), ("carcass", 3), ("dumped", 2), ("bins", 2),
    ],
    "Noise": [
        ("noise", 3), ("music", 3), ("amplifier", 3), ("drilling", 3),
        ("loud", 2), ("band playing", 2), ("idling", 2),
    ],
    "Road Damage": [
        ("crack", 3), ("sink", 3), ("subsidence", 3), ("subsided", 3),
        ("buckled", 3), ("collapse", 3), ("crater", 3), ("upturned", 3),
        ("footpath", 2), ("manhole", 2), ("broken", 1),
    ],
    "Heritage Damage": [
        ("heritage damage", 4), ("heritage", 3), ("historic", 3),
        ("monument", 3), ("defaced", 2),
    ],
    "Heat Hazard": [
        ("heat", 3), ("temperature", 3), ("melting", 3), ("bubbling", 3),
        ("\u00b0c", 3), ("scorching", 3), ("burns", 2),
    ],
    "Drain Blockage": [
        ("drain blockage", 4), ("drain blocked", 4), ("blocked drain", 4),
        ("drain", 2), ("clogged", 3), ("choked", 3), ("manhole overflow", 3),
    ],
}


def _find_matches(text, keyword):
    """Return starting offsets of every case-insensitive occurrence."""
    positions = []
    lowered = text.lower()
    start = 0
    while True:
        idx = lowered.find(keyword.lower(), start)
        if idx == -1:
            return positions
        positions.append(idx)
        start = idx + len(keyword)


def classify_complaint(row):
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag
    """
    if row is None:
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "Malformed row: no data available.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    # --- Category scoring -------------------------------------------------
    scores = {}
    evidence = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        hits = []
        for keyword, weight in keywords:
            found = _find_matches(description, keyword)
            if found:
                score += weight * len(found)
                hits.append(keyword)
        if score > 0:
            scores[category] = score
            evidence[category] = hits

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))

    ambiguous = False
    # A top score below 2 means only a weak signal matched — not enough
    # to classify confidently.
    if not ranked or ranked[0][1] < 2:
        category = "Other"
        matched_words = []
        ambiguous = True
    else:
        category = ranked[0][0]
        matched_words = evidence[category]
        # Tie between top two categories -> genuinely ambiguous.
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            ambiguous = True

    # --- Priority ---------------------------------------------------------
    severity_hits = []
    for keyword in SEVERITY_KEYWORDS:
        if _find_matches(description, keyword):
            severity_hits.append(keyword)

    if severity_hits:
        priority = "Urgent"
    elif any(_find_matches(description, m) for m in LOW_PRIORITY_MARKERS):
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason (must cite specific words from the description) ----------
    citable = [w for w in matched_words if w[:1].isalpha()]
    cited = ", ".join('"%s"' % w for w in sorted(set(citable))[:3])
    if category == "Other":
        reason = (
            "No known category keywords found in the description; "
            "classified as Other pending human review."
        )
    elif cited:
        reason = (
            "Classified as %s based on %s in the description."
            % (category, cited)
        )
    else:
        reason = "Classified as %s from the description." % category

    if severity_hits:
        reason += (
            " Priority Urgent due to severity keyword(s): %s."
            % ", ".join('"%s"' % w for w in sorted(set(severity_hits)))
        )

    # --- Flag -------------------------------------------------------------
    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on bad rows, always produces output.
    Returns the number of rows written.
    """
    results = []
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            required = {"complaint_id", "description"}
            fieldnames = reader.fieldnames or []
            missing = required - set(fieldnames)
            if missing:
                raise ValueError(
                    "Input CSV is missing required column(s): %s"
                    % ", ".join(sorted(missing))
                )
            for line_no, row in enumerate(reader, start=2):
                try:
                    results.append(classify_complaint(row))
                except Exception as exc:  # never crash on one bad row
                    results.append({
                        "complaint_id": (row or {}).get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row failed classification: %s" % exc,
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print("ERROR: input file not found: %s" % input_path, file=sys.stderr)
        raise SystemExit(1)
    except UnicodeDecodeError:
        print("ERROR: could not decode %s as UTF-8" % input_path,
              file=sys.stderr)
        raise SystemExit(1)

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    print("Classified %d complaint(s): %d Urgent, %d NEEDS_REVIEW"
          % (len(results), urgent, flagged))
    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
