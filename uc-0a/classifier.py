"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and review flag.
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

CATEGORY_KEYWORDS = {
    "Pothole": [r"\bpothole", r"\bpotholes?\b", r"\broad\s*hole"],
    "Flooding": [r"\bflood", r"\bwaterlog", r"\binundat", r"\bsubmerg"],
    "Streetlight": [r"\bstreet\s*light", r"\blamp\s*post", r"\blight\s*out", r"\bstreetlamp", r"\blights?\s+out", r"\bunlit", r"\bdarkness", r"\bcolony.*dark", r"\bsubstation\s*tripped"],
    "Waste": [r"\bwaste", r"\bgarbage", r"\btrash", r"\brefuse", r"\blitter", r"\bdump", r"\bdead\s+animal", r"\bnot\s+removed", r"\boverflow(?:ing)?\s+(?:garbage|waste|bin)"],
    "Noise": [r"\bnoise", r"\bloud", r"\bhonking", r"\bblast", r"\bdj\b", r"\bfireworks?\b", r"\bplaying\s+music", r"\bvenue\s+playing", r"\bband\s+playing", r"\bmusic\s+audible", r"\bamplifier"],
    "Heritage Damage": [r"\bheritage", r"\bmonument", r"\bhistorical", r"\bancient", r"\bmemorial", r"\btram\s*road", r"\bstep\s*well"],
    "Heat Hazard": [r"\bheat", r"\bheatwave", r"\bsunstroke", r"\bdehydrat", r"\bextreme\s*heat", r"\bmelting", r"\btemperature", r"\bunbearable", r"\b\°C", r"\bburn"],
    "Road Damage": [r"\broad\s*damage", r"\bcrack", r"\broad\s*surface", r"\bfootpath", r"\bsidewalk", r"\btil[es]+\s+(?:broken|upturned|damaged|cracked)", r"\bcobblestone", r"\bpaving", r"\bbuckl"],
    "Drain Blockage": [r"\bdrain", r"\bclog", r"\bsewage", r"\bmanhole", r"\bstorm\s*water"],
}

URGENCY_EXTRACT = re.compile(
    r"(injur|child|school|hospital|ambulance|fire|hazard|fell|collaps)",
    re.IGNORECASE,
)

CATEGORY_EXTRACT = {
    cat: re.compile("|".join(patterns), re.IGNORECASE)
    for cat, patterns in CATEGORY_KEYWORDS.items()
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description") or ""
    desc = description.strip()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description field is empty so no complaint type could be identified.",
            "flag": "NEEDS_REVIEW",
        }

    matches = []
    for cat, regex in CATEGORY_EXTRACT.items():
        if regex.search(desc):
            matches.append(cat)

    if len(matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matches) == 1:
        category = matches[0]
        flag = ""
    else:
        category = matches[0]
        flag = "NEEDS_REVIEW"

    priority = "Low"
    if URGENCY_EXTRACT.search(desc):
        priority = "Urgent"
    elif any(kw in desc.lower() for kw in ["damaged", "broken", "risk", "danger"]):
        priority = "Standard"

    reason = _build_reason(desc, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(desc: str, category: str) -> str:
    desc_lower = desc.lower()

    if category == "Other":
        snippet = desc[:80].rstrip(".")
        return f"No specific category keywords found in the description mentioning \"{snippet}\"."

    regex = CATEGORY_EXTRACT[category]
    match = regex.search(desc)
    if match:
        start = max(0, match.start() - 20)
        end = min(len(desc), match.end() + 20)
        snippet = desc[start:end].strip()
        return f"The description mentions \"{snippet}\" which indicates a {category} issue."

    return f"The description indicates a {category} complaint."


def batch_classify(input_path: str, output_path: str):
    failed = 0
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if not row.get("description"):
                        row["description"] = ""
                    results.append(classify_complaint(row))
                except Exception:
                    failed += 1
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Row data incomplete or malformed.",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

    if failed:
        print(f"Warning: {failed} row(s) failed classification and were flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
