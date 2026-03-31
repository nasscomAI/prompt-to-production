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

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole(?:s)?\b"],
    "Flooding": [r"\bflood(?:ing|ed|s)?\b", r"\bwater\s+logging\b", r"\bwaterlogged\b"],
    "Streetlight": [r"\bstreet\s*light(?:s)?\b", r"\blight\s*post(?:s)?\b", r"\blamp\s*post(?:s)?\b"],
    "Waste": [r"\bgarbage\b", r"\btrash\b", r"\bwaste\b", r"\bdumping\b", r"\blitter\b"],
    "Noise": [r"\bnoise\b", r"\bloud\b", r"\bhonking\b", r"\bconstruction\s+noise\b"],
    "Road Damage": [r"\broad\s+damage\b", r"\bbroken\s+road\b", r"\bcracked\s+road\b", r"\broad\s+crack\b"],
    "Heritage Damage": [r"\bheritage\b", r"\bmonument\b", r"\bhistoric(?:al)?\b", r"\bold\s+structure\b"],
    "Heat Hazard": [r"\bheat\b", r"\bheatwave\b", r"\bhigh\s+temperature\b", r"\bsunstroke\b"],
    "Drain Blockage": [r"\bdrain(?:s)?\b", r"\bdrainage\b", r"\bblocked\s+drain(?:s)?\b", r"\bsewer\s+block(?:ed|age)?\b"],
}


def _get_description(row: dict) -> str:
    for key in ("description", "complaint_description", "details", "text"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _find_severity_tokens(text: str) -> list:
    found = []
    for token in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(token)}\b", text, flags=re.IGNORECASE):
            found.append(token)
    return found


def _detect_categories(text: str) -> dict:
    matches = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            m = re.search(pattern, text, flags=re.IGNORECASE)
            if m:
                matches[category] = m.group(0)
                break
    return matches


def _one_sentence_reason(reason: str) -> str:
    cleaned = " ".join(str(reason).split())
    cleaned = cleaned.rstrip(".!? ")
    return f"{cleaned}."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implements UC-0A RICE constraints from agents.md/skills.md/README.md.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = _get_description(row)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": _one_sentence_reason(
                "Category set to Other because description is missing and cannot support a specific category"
            ),
            "flag": "NEEDS_REVIEW",
        }

    severity_hits = _find_severity_tokens(description)
    priority = "Urgent" if severity_hits else "Standard"

    category_hits = _detect_categories(description)
    if len(category_hits) == 1:
        category = next(iter(category_hits.keys()))
        flag = ""
        evidence = next(iter(category_hits.values()))
        if severity_hits:
            reason = _one_sentence_reason(
                f"Category set to {category} from '{evidence}' and priority set to Urgent from '{severity_hits[0]}'"
            )
        else:
            reason = _one_sentence_reason(
                f"Category set to {category} from '{evidence}' and priority set to Standard because no severity keyword was found"
            )
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(category_hits) > 1:
            sampled = ", ".join([f"'{v}'" for v in list(category_hits.values())[:2]])
            if severity_hits:
                reason = _one_sentence_reason(
                    f"Category set to Other because description is ambiguous across {sampled} and priority set to Urgent from '{severity_hits[0]}'"
                )
            else:
                reason = _one_sentence_reason(
                    f"Category set to Other because description is ambiguous across {sampled} and priority set to Standard"
                )
        else:
            first_words = " ".join(description.split()[:6])
            if severity_hits:
                reason = _one_sentence_reason(
                    f"Category set to Other because '{first_words}' does not match an allowed category and priority set to Urgent from '{severity_hits[0]}'"
                )
            else:
                reason = _one_sentence_reason(
                    f"Category set to Other because '{first_words}' does not match an allowed category and priority set to Standard"
                )

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in {"Urgent", "Standard", "Low"}:
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
    
    Read input CSV, classify each row, write results CSV without crashing on bad rows.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as in_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as out_file:
        reader = csv.DictReader(in_file)
        writer = csv.DictWriter(out_file, fieldnames=output_fields)
        writer.writeheader()

        for idx, row in enumerate(reader, start=1):
            try:
                if row is None:
                    raise ValueError("Row is null")
                result = classify_complaint(row)
                if not result.get("complaint_id"):
                    result["complaint_id"] = str(row.get("complaint_id", "")).strip() or str(idx)
            except Exception as exc:
                raw_id = ""
                if isinstance(row, dict):
                    raw_id = str(row.get("complaint_id", "")).strip()
                result = {
                    "complaint_id": raw_id or str(idx),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": _one_sentence_reason(
                        f"Category set to Other because row processing failed with '{str(exc)}'"
                    ),
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow({k: result.get(k, "") for k in output_fields})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
