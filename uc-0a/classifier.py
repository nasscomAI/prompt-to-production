"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import sys

# ── Taxonomy ──────────────────────────────────────────────────────────────────

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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# keyword → category mappings (checked in order; first match wins)
CATEGORY_RULES = [
    (["pothole"],                                   "Pothole"),
    (["flood", "flooded", "flooding", "waterlog"],  "Flooding"),
    (["streetlight", "street light", "lamp", "light out", "no light", "dark road"], "Streetlight"),
    (["waste", "garbage", "trash", "litter", "dump", "rubbish", "bin"],             "Waste"),
    (["noise", "loud", "sound", "music", "party", "horn"],                          "Noise"),
    (["road damage", "road crack", "broken road", "damaged road", "road broken"],   "Road Damage"),
    (["heritage", "monument", "historical", "ancient", "fort", "temple damage"],    "Heritage Damage"),
    (["heat", "hot", "temperature", "heat wave", "heat hazard"],                    "Heat Hazard"),
    (["drain block", "drain choke", "blocked drain", "clogged drain", "drain overflow", "drain"], "Drain Blockage"),
]


# ── Core logic ────────────────────────────────────────────────────────────────

def _detect_category(description: str) -> tuple[str, bool]:
    """
    Returns (category, is_ambiguous).
    is_ambiguous is True when no rule matches and we fall through to Other.
    """
    lower = description.lower()
    matched = []
    for keywords, category in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    if len(matched) > 1:
        # Multiple matches — return the first but flag for review
        return matched[0], True
    return "Other", True


def _detect_priority(description: str) -> tuple[str, str | None]:
    """
    Returns (priority, triggering_keyword_or_None).
    Urgent if any severity keyword found; otherwise Standard.
    """
    lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in lower:
            return "Urgent", kw
    return "Standard", None


def _build_reason(description: str, category: str, priority: str, trigger_kw: str | None) -> str:
    """One sentence citing specific words from description."""
    # Pull up to the first sentence of the description as evidence
    excerpt = description.split(".")[0].strip()
    if trigger_kw:
        return (
            f"Classified as {category} / {priority} because description mentions "
            f'"{trigger_kw}" in: "{excerpt}".'
        )
    return f'Classified as {category} based on: "{excerpt}".'


# ── Public skills ─────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    # Empty description edge-case (per skills.md)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority, trigger_kw = _detect_priority(description)

    # Severity present but category unclear → still Urgent + NEEDS_REVIEW
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    reason = _build_reason(description, category, priority, trigger_kw)

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
    Continues on bad rows; logs failures to stderr.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not parse input file: {exc}", file=sys.stderr)
        sys.exit(1)

    output_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]
    results = []

    for idx, row in enumerate(rows):
        try:
            classification = classify_complaint(row)
        except Exception as exc:
            print(f"WARNING: Row {idx} failed classification: {exc}", file=sys.stderr)
            classification = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Classification error — manual review required.",
                "flag": "NEEDS_REVIEW",
            }

        out_row = dict(row)
        out_row["category"] = classification["category"]
        out_row["priority"] = classification["priority"]
        out_row["reason"] = classification["reason"]
        out_row["flag"] = classification["flag"]
        results.append(out_row)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
