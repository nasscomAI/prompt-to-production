"""
UC-0A — Complaint Classifier

Reads a city complaint CSV, classifies each row against the fixed taxonomy
in uc-0a/README.md, and writes a results CSV. Behaviour follows the
enforcement rules in agents.md:

- category is an exact string from the 10-value enum (taxonomy drift guard)
- priority is Urgent whenever a severity keyword appears in the description
  (severity blindness guard), otherwise Standard
- every row gets a one-sentence reason quoting words from the description
  (missing justification guard)
- ambiguous or unclassifiable rows are flagged NEEDS_REVIEW instead of
  guessed confidently (false confidence guard)
- batch mode never crashes on bad rows and flags nulls instead of skipping
"""
import argparse
import csv
import re

CATEGORY_ENUM = [
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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

SEVERITY_RE = re.compile(
    r"\b(?:" + "|".join(SEVERITY_KEYWORDS) + r")\w*", re.IGNORECASE
)

CATEGORY_EVIDENCE = {
    "Heritage Damage": [r"heritage"],
    "Heat Hazard": [r"heat\s?wave", r"heat\s?hazard", r"heatwave", r"extreme\s+heat"],
    "Flooding": [r"flood\w*", r"waterlog\w*", r"knee[- ]deep", r"standing in water"],
    "Drain Blockage": [
        r"drains?\s+(?:is\s+|are\s+)?blocked",
        r"(?:blocked|clogged|overflowing)\s+drains?",
        r"drain\s+block\w*",
    ],
    "Streetlight": [r"street\s?-?lights?\b", r"lights?\s+out", r"light\s+poles?"],
    "Pothole": [r"pot\s?holes?"],
    "Noise": [r"\bnoise\b", r"\bnoisy\b", r"\bloud\b", r"\bmusic\b"],
    "Waste": [
        r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\blitter\w*",
        r"\bdump(?:ed|ing)?\b", r"dead\s+animal",
    ],
    "Road Damage": [
        r"road\s+surface", r"road\s+damage", r"\bcrack\w*", r"\bsinking\b",
        r"\bmanholes?\b", r"\bfootpath\w*", r"\btiles?\b", r"\bupturned\b",
        r"\bbroken\b",
    ],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty; no classification possible.",
            "flag": "NEEDS_REVIEW",
        }

    scores = {}
    evidence = {}
    for category, patterns in CATEGORY_EVIDENCE.items():
        hits = []
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                hits.append(match.group(0))
        if hits:
            scores[category] = len(hits)
            evidence[category] = hits

    best_score = max(scores.values()) if scores else 0
    winners = [c for c, s in scores.items() if s == best_score] if best_score else []
    ambiguous = len(winners) > 1
    category = winners[0] if winners else "Other"

    severity_hits = SEVERITY_RE.findall(description)
    priority = "Urgent" if severity_hits else "Standard"

    if not winners:
        reason = "No enum category has textual evidence in this description; routed for manual review."
    else:
        quoted = ", ".join("'%s'" % hit for hit in evidence[category])
        reason = "%s inferred from description terms %s; no severity signals present, priority Standard." % (
            category,
            quoted,
        )
        if severity_hits:
            severity_quoted = ", ".join("'%s'" % hit for hit in severity_hits)
            reason = "%s inferred from description terms %s; priority Urgent triggered by severity signal(s) %s." % (
                category,
                quoted,
                severity_quoted,
            )

    flag = "NEEDS_REVIEW" if (ambiguous or category == "Other") else ""

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
    Flags nulls, never crashes on bad rows, produces output even if some rows fail.
    """
    results = []
    null_report = {"missing_complaint_id": 0, "missing_description": 0, "failed_rows": 0}

    with open(input_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)
            except Exception as error:
                null_report["failed_rows"] += 1
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification failed (%s); routed for manual review." % error.__class__.__name__,
                    "flag": "NEEDS_REVIEW",
                }
            if not result["complaint_id"]:
                null_report["missing_complaint_id"] += 1
                result["complaint_id"] = "ROW-%d" % line_number
            if not (row.get("description") or "").strip():
                null_report["missing_description"] += 1
            results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    summary = build_summary(results, null_report)
    return {"rows": len(results), "null_report": null_report, "summary": summary}


def build_summary(results, null_report):
    """Aggregate counts for the printed run report."""
    category_counts = {}
    priority_counts = {}
    flagged = 0
    for result in results:
        category_counts[result["category"]] = category_counts.get(result["category"], 0) + 1
        priority_counts[result["priority"]] = priority_counts.get(result["priority"], 0) + 1
        if result["flag"] == "NEEDS_REVIEW":
            flagged += 1
    return {
        "categories": category_counts,
        "priorities": priority_counts,
        "needs_review": flagged,
        "nulls": null_report,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    outcome = batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)
    print("Rows classified: %d" % outcome["rows"])
    print("Category counts: %s" % outcome["summary"]["categories"])
    print("Priority counts: %s" % outcome["summary"]["priorities"])
    print("Rows flagged NEEDS_REVIEW: %d" % outcome["summary"]["needs_review"])
    print("Null/failure report: %s" % outcome["summary"]["nulls"])
