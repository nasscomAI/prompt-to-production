"""
UC-0A — Complaint Classifier
Rule-based classifier built from agents.md and skills.md.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}

SEVERITY_KEYWORDS = [
    r"\binjur", r"\bchild", r"\bschool", r"\bhospital", r"\bambulance",
    r"\bfire", r"\bhazard", r"\bfell\b", r"\bcollapse",
]

LOW_TRIGGERS = [
    r"\bresolved", r"\bfixed", r"\bno longer", r"\binactive", r"\binformational",
]

CATEGORY_SIGNALS = {
    "Pothole": [r"\bpothole", r"\bpot hole"],
    "Flooding": [r"\bflood", r"\bwaterlog", r"\bknee-deep", r"\bstanding in water", r"\binundat", r"\bsubmerg"],
    "Streetlight": [r"\bstreetlight", r"\bstreet light", r"\bstreet lamp", r"\blights? out", r"\bflicker", r"\bspark"],
    "Waste": [r"\bgarbage", r"\bwaste", r"\brubbish", r"\btrash", r"\blitter", r"\bbins?", r"\bdead animal", r"\brefuse"],
    "Noise": [r"\bnoise", r"\bmusic", r"\bloud", r"\bparty", r"\bhonk", r"\bbark", r"\bshout"],
    "Road Damage": [r"\bcracked", r"\bsinking", r"\bmanhole", r"\bfootpath", r"\broad surface", r"\bsinkhole", r"\bpavement"],
    "Heritage Damage": [r"\bheritage", r"\bmonument", r"\bhistoric"],
    "Heat Hazard": [r"\bheat", r"\bheatwave", r"\bscorching", r"\bsweltering"],
    "Drain Blockage": [r"\bdrain", r"\bsewer", r"\bdrainage", r"\bclogg"],
}


def _detect_category(text: str) -> tuple:
    counts = {}
    phrases = []
    for category, patterns in CATEGORY_SIGNALS.items():
        hits = []
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hits.append(match.group(0).strip())
        if hits:
            counts[category] = len(hits)
            phrases.extend(hits)
    if not counts:
        return "Other", [], counts
    top = max(counts.values())
    tops = [c for c, n in counts.items() if n == top]
    if len(tops) == 1:
        return tops[0], phrases, counts
    return "Other", phrases, counts


def _priority(text: str) -> str:
    for pattern in SEVERITY_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return "Urgent"
    for pattern in LOW_TRIGGERS:
        if re.search(pattern, text, re.IGNORECASE):
            return "Low"
    return "Standard"


def _unique(phrases: list) -> list:
    seen = set()
    result = []
    for phrase in phrases:
        if phrase not in seen:
            seen.add(phrase)
            result.append(phrase)
    return result


def _build_reason(phrases: list, category: str, counts: dict) -> str:
    if category == "Other" and not counts:
        return "No category signal found in the description, so it is under-specified."
    quoted = " and ".join(f'"{p}"' for p in _unique(phrases)[:4])
    if category == "Other":
        return f"Description contains {quoted}, so the category is ambiguous."
    if len(counts) > 1:
        others = " and ".join(sorted(c for c in counts if c != category))
        return f'Description contains {quoted}; it is mostly "{category}" but also mentions {others}.'
    return f"Description contains {quoted}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty or missing.",
            "flag": "NEEDS_REVIEW",
        }
    text = description.lower()
    category, phrases, counts = _detect_category(text)
    if category == "Other" or len(counts) > 1:
        flag = "NEEDS_REVIEW"
    else:
        flag = ""
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": _priority(text),
        "reason": _build_reason(phrases, category, counts),
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
    except OSError as exc:
        print(f"Could not read {input_path}: {exc}")
        return
    results = [classify_complaint(row) for row in rows]
    flagged = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    print(f"Classified {len(results)} rows, {flagged} flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
