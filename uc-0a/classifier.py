"""UC-0A complaint classifier built from the documented RICE rules."""

import argparse
import csv
import re


CATEGORY_RULES = (
    ("Pothole", (r"\bpotholes?\b",)),
    ("Flooding", (r"\bflood\w*\b", r"\brainwater\b", r"\brain water\b", r"\brain\b")),
    (
        "Streetlight",
        (
            r"\bstreetlights?\b",
            r"\bstreet lights?\b",
            r"\blamp posts?\b",
            r"\bunlit\b",
            r"\blights? out\b",
            r"\bdarkness\b",
        ),
    ),
    ("Waste", (r"\bgarbage\b", r"\bwaste\b", r"\bdead animal\b", r"\brefuse\b", r"\bdumped\b", r"\blitter\b")),
    ("Noise", (r"\bmusic\b", r"\bdrilling\b", r"\bnoise\b", r"\bsound\b", r"\bidling\b", r"\bamplifier\b", r"\bwedding band\b")),
    (
        "Road Damage",
        (
            r"\broad surface\b",
            r"\bpaving\b",
            r"\bfootpath\b",
            r"\bcobblestones?\b",
            r"\bcrater\b",
            r"\bsubsid\w*\b",
            r"\bcollaps\w*\b",
            r"\bbuckl\w*\b",
            r"\btiles? broken\b",
            r"\bstep well\b",
        ),
    ),
    ("Heritage Damage", (r"\bheritage\b", r"\bhistoric\b", r"\bancient\b", r"\bmuseum\b")),
    (
        "Heat Hazard",
        (
            r"\bmelting\b",
            r"\btemperature\b",
            r"\bheat\w*\b",
            r"\bsun\b",
            r"\bhot\b",
            r"\bburn\w*\b",
            r"°c",
        ),
    ),
    ("Drain Blockage", (r"\bdrains?\b", r"\bmanhole\b", r"\bsewer\b", r"\bdrainage\b")),
)

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

OUTPUT_FIELDS = ("complaint_id", "category", "priority", "reason", "flag")


def _first_match(description: str, patterns: tuple[str, ...]) -> str | None:
    """Return the exact text that matched the first applicable pattern."""
    for pattern in patterns:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def classify_complaint(row: dict) -> dict:
    """Classify one complaint into the required output schema."""
    if not isinstance(row, dict):
        row = {}

    complaint_id = str(row.get("complaint_id") or "").strip()
    description = str(row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty description requires manual review.",
            "flag": "NEEDS_REVIEW",
        }

    matches = []
    for category, patterns in CATEGORY_RULES:
        evidence = _first_match(description, patterns)
        if evidence:
            matches.append((category, evidence))

    # Pothole is more specific than Road Damage, so it wins that overlap.
    matched_names = {category for category, _ in matches}
    if "Pothole" in matched_names and "Road Damage" in matched_names:
        matches = [match for match in matches if match[0] != "Road Damage"]

    flag = ""
    if not matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        excerpt = re.sub(r"[.!?;]+", "", description[:60]).strip()
        reason = (
            f"Could not map description text '{excerpt}' to an allowed category "
            "and flagged it for review"
        )
    elif len(matches) == 1:
        category, evidence = matches[0]
        reason = f"Classified as {category} because the description contains '{evidence}'"
    else:
        category = matches[0][0]
        flag = "NEEDS_REVIEW"
        evidence = " and ".join(
            f"{matched_category} from '{matched_text}'"
            for matched_category, matched_text in matches
        )
        reason = (
            f"Matched {evidence}; defaulted to {category} and flagged it for review"
        )

    severity_matches = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if re.search(rf"\b{re.escape(keyword)}", description, flags=re.IGNORECASE)
    ]
    if severity_matches:
        priority = "Urgent"
        quoted_keywords = ", ".join(f"'{keyword}'" for keyword in severity_matches)
        reason += (
            f"; priority is Urgent because the description contains {quoted_keywords}"
        )
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": f"{reason}.",
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Classify every CSV row while preserving invalid rows for review."""
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            for row in csv.DictReader(infile):
                try:
                    results.append(classify_complaint(row))
                except Exception as error:  # Keep processing after a malformed row.
                    complaint_id = str(row.get("complaint_id") or "UNKNOWN").strip()
                    safe_error = re.sub(r"[.!?;\r\n]+", " ", str(error)).strip()
                    results.append(
                        {
                            "complaint_id": complaint_id,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Classification failed because '{safe_error}' and requires manual review.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
    except Exception as error:
        print(f"Critical read error: {error}")

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    arguments = parser.parse_args()
    batch_classify(arguments.input, arguments.output)
    print(f"Done. Results written to {arguments.output}")