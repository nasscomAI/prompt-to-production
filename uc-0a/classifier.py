"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


ALLOWED_CATEGORIES = [
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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_KEYWORDS = {
    "Pothole": {"pothole", "crater"},
    "Flooding": {"flood", "flooded", "waterlogged", "water logging", "inundated"},
    "Streetlight": {"streetlight", "streetlights", "lights out", "flickering", "dark", "sparking"},
    "Waste": {"garbage", "trash", "waste", "litter", "dumped", "dead animal", "bins"},
    "Noise": {"noise", "loud", "music", "midnight", "speaker"},
    "Road Damage": {"road surface", "cracked", "sinking", "tiles broken", "upturned", "damaged road", "footpath"},
    "Heritage Damage": {"heritage", "monument", "historic", "old city"},
    "Heat Hazard": {"heat", "heatwave", "sunstroke", "dehydration"},
    "Drain Blockage": {"drain blocked", "drainage", "clogged drain", "manhole", "sewer"},
}

LOW_PRIORITY_HINTS = {
    "noise",
    "music",
    "midnight",
    "smell",
    "odour",
    "odor",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _matched_keywords(text: str, keywords: set[str]) -> list[str]:
    hits = []
    for kw in keywords:
        if kw in text:
            hits.append(kw)
    return sorted(hits)


def _pick_category(text: str) -> tuple[str, list[str], bool]:
    scores = {}
    evidence = {}

    for category, words in CATEGORY_KEYWORDS.items():
        hits = _matched_keywords(text, words)
        scores[category] = len(hits)
        evidence[category] = hits

    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        return "Other", [], True

    winners = [cat for cat, score in scores.items() if score == max_score]
    if len(winners) > 1:
        merged_evidence = sorted({kw for cat in winners for kw in evidence[cat]})
        return "Other", merged_evidence, True

    winner = winners[0]
    return winner, evidence[winner], False


def _pick_priority(text: str, category: str) -> tuple[str, list[str]]:
    severity_hits = _matched_keywords(text, SEVERITY_KEYWORDS)
    if severity_hits:
        return "Urgent", severity_hits

    low_hits = _matched_keywords(text, LOW_PRIORITY_HINTS)
    if low_hits and category in {"Noise", "Waste"}:
        return "Low", low_hits

    return "Standard", []


def _build_reason(category: str, priority: str, evidence_words: list[str], desc_excerpt: str) -> str:
    if evidence_words:
        evidence = ", ".join(f"'{w}'" for w in evidence_words[:3])
        return f"Classified as {category} with {priority} priority based on words {evidence} in the description."

    excerpt = desc_excerpt[:80].strip()
    if excerpt:
        return f"Classified as {category} with {priority} priority using description text '{excerpt}'."

    return f"Classified as {category} with {priority} priority because the complaint details are limited."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A taxonomy, urgency keywords, reason requirement, and ambiguity flagging.
    """
    complaint_id = (row or {}).get("complaint_id", "")
    description_raw = (row or {}).get("description", "")
    description = _normalize_text(description_raw)

    if not description:
        reason = "Classified as Other with Standard priority because the description is missing."
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    category, category_evidence, ambiguous = _pick_category(description)
    priority, severity_evidence = _pick_priority(description, category)

    evidence_words = severity_evidence or category_evidence
    reason = _build_reason(category, priority, evidence_words, description_raw)

    flag = "NEEDS_REVIEW" if ambiguous else ""
    if ambiguous:
        reason = "Classified as Other because the description maps to multiple or unclear categories."

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

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
    rows_processed = 0
    rows_flagged = 0

    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV is missing headers.")

        input_fields = list(reader.fieldnames)
        output_fields = input_fields + [
            field for field in ["category", "priority", "reason", "flag"] if field not in input_fields
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                rows_processed += 1
                try:
                    cls = classify_complaint(row)
                except Exception as exc:
                    cls = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classified as Other due to row processing error: {str(exc)}.",
                        "flag": "NEEDS_REVIEW",
                    }

                if cls.get("flag") == "NEEDS_REVIEW":
                    rows_flagged += 1

                merged = dict(row)
                merged.update({
                    "category": cls.get("category", "Other"),
                    "priority": cls.get("priority", "Standard"),
                    "reason": cls.get("reason", "Classified as Other with Standard priority."),
                    "flag": cls.get("flag", ""),
                })
                writer.writerow(merged)

    return {
        "rows_processed": rows_processed,
        "rows_flagged": rows_flagged,
        "output_path": output_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    summary = batch_classify(args.input, args.output)
    print(
        "Done. "
        f"Rows processed: {summary['rows_processed']}, "
        f"rows flagged: {summary['rows_flagged']}. "
        f"Results written to {args.output}"
    )
