"""
UC-0A — Complaint Classifier
Classifies citizen complaints into the exact taxonomy defined in README.md.
Rules enforced here mirror agents.md:
  - category: exact allowed strings only
  - priority: Urgent when a severity keyword is present
  - reason:   one sentence citing specific words from the description
  - flag:     NEEDS_REVIEW when classification is genuinely ambiguous
"""
import argparse
import csv
import re
import sys

CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_STEMS = [
    "injur", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collaps",
]

LOW_SIGNAL_MARKERS = ["minor", "cosmetic", "aesthetic", "not urgent", "no injuries"]

STRONG_KEYWORDS = {"pothole", "flood", "waterlog", "water logging",
                   "inundat", "submerg"}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlog", "water logging", "inundat", "submerg",
                 "rainwater"],
    "Streetlight": ["streetlight", "street light", "streetlights", "street lights",
                    "lamp post", "light pole", "lights out", "flickering", "sparking",
                    "electrical hazard", "unlit", "darkness", "power cut",
                    "power outage", "blackout"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumped", "dumping",
              "dead animal", "overflowing bins", "bins overflowing"],
    "Noise": ["noise", "loud", "music", "loudspeaker", "amplifier",
              "wedding band", "band playing", "drilling", "sound"],
    "Road Damage": ["road surface", "cracked", "cracks", "sinking", "manhole",
                    "footpath", "pavement", "paving", "tiles broken",
                    "broken tiles", "upturned", "sinkhole", "cave-in",
                    "crater", "collapsed", "collapse", "subsided",
                    "subsidence"],
    "Heritage Damage": ["heritage", "historic", "monument", "statue",
                        "memorial", "museum", "defaced", "knocked over"],
    "Heat Hazard": ["heat wave", "heatwave", "heat stroke", "sunstroke",
                    "dehydrat", "extreme heat", "heat", "temperature",
                    "melting"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drains blocked",
                       "drainage blocked", "clogged", "choked", "blockage",
                       "blocked", "stormwater drain", "drain overflow"],
}


def _tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def _contains_phrase(text_lower, phrase):
    pattern = r"\b" + re.escape(phrase).replace(r"\ ", r"\s+") + r"\w*"
    return re.search(pattern, text_lower) is not None


def _keyword_weight(keyword):
    return 2 if keyword in STRONG_KEYWORDS else 1


def _find_matches(text):
    text_lower = text.lower()
    found = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if _contains_phrase(text_lower, kw)]
        if hits:
            found[category] = hits
    return found


def _score(matches):
    return {cat: sum(_keyword_weight(kw) for kw in hits)
            for cat, hits in matches.items()}


def _find_severity(text):
    text_lower = text.lower()
    words = set(_tokens(text_lower))
    hits = []
    for stem in SEVERITY_STEMS:
        if any(w.startswith(stem) for w in words):
            hits.append(stem)
    return hits


def classify_complaint(row):
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag.
    Never raises on bad input — returns Other + NEEDS_REVIEW instead.
    """
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip()
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": "",
    }

    if not description:
        result["reason"] = ("No complaint description provided; cannot determine "
                            "category.")
        result["flag"] = "NEEDS_REVIEW"
        return result

    matches = _find_matches(description)
    severity_hits = _find_severity(description)
    weights = _score(matches)

    scored = sorted(matches.items(), key=lambda kv: (-weights[kv[0]],
                                                     CATEGORIES.index(kv[0])))
    ambiguous = False
    if not matches:
        category = "Other"
        cited_words = []
    else:
        top_cat, top_hits = scored[0]
        category = top_cat
        cited_words = list(top_hits)
        if len(scored) > 1 and weights[scored[0][0]] == weights[scored[1][0]]:
            runner_cat, runner_hits = scored[1]
            ambiguous = True
            cited_words += [kw for kw in runner_hits if kw not in cited_words]

    if severity_hits:
        priority = "Urgent"
    elif any(marker in description.lower() for marker in LOW_SIGNAL_MARKERS):
        priority = "Low"
    else:
        priority = "Standard"

    evidence = ", ".join("'%s'" % w for w in cited_words[:4]) or "no matching keywords"
    reason = "Description mentions %s -> classified as %s." % (evidence, category)
    if priority == "Urgent" and severity_hits:
        sev = ", ".join(sorted(set(severity_hits)))
        reason += " Priority Urgent due to severity keyword(s): %s." % sev

    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    if ambiguous or category == "Other":
        result["flag"] = "NEEDS_REVIEW"
    return result


def batch_classify(input_path, output_path):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on malformed rows, and always produces output.
    Returns a summary dict of counts for reporting.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
    except OSError as exc:
        print("ERROR: cannot read input file '%s': %s" % (input_path, exc),
              file=sys.stderr)
        raise SystemExit(1)

    if "description" not in fieldnames:
        print("ERROR: input CSV is missing required column 'description'. "
              "Columns found: %s" % (fieldnames or "none"), file=sys.stderr)
        raise SystemExit(1)

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    summary = {"total": len(rows), "urgent": 0, "needs_review": 0, "failed": 0}

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for index, row in enumerate(rows, start=2):
            try:
                result = classify_complaint(row)
                if not result["complaint_id"]:
                    result["complaint_id"] = "row-%d" % index
            except Exception as exc:
                summary["failed"] += 1
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip()
                                    or "row-%d" % index,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification failed: %s." % exc,
                    "flag": "NEEDS_REVIEW",
                }
            if result["priority"] == "Urgent":
                summary["urgent"] += 1
            if result["flag"] == "NEEDS_REVIEW":
                summary["needs_review"] += 1
            writer.writerow({k: result[k] for k in out_fields})

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    stats = batch_classify(args.input, args.output)
    print("Classified %d complaints | Urgent: %d | NEEDS_REVIEW: %d | Failed: %d"
          % (stats["total"], stats["urgent"], stats["needs_review"],
             stats["failed"]))
    print("Done. Results written to %s" % args.output)
