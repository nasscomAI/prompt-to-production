"""UC-0A Complaint Classifier.

Maps exactly one citizen complaint row to the fixed UC-0A schema:
category, priority, reason, flag. Never modifies the input row, never drops
rows, and refuses confidently on ambiguity (category Other + flag
NEEDS_REVIEW when the description alone does not point to one category).
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
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
}

# --- Severity: any of these in the description MUST produce Urgent priority. ---
SEVERITY_PATTERNS = [
    re.compile(r"\binjur(?:y|ies)\b"),
    re.compile(r"\bchild(?:ren)?\b"),
    re.compile(r"\bschools?\b"),
    re.compile(r"\bhospit\w*\b"),          # hospital, hospitalised, ...
    re.compile(r"\bambulances?\b"),
    re.compile(r"\bfires?\b"),
    re.compile(r"\bhazards?\b"),
    re.compile(r"\bfell\b"),
    re.compile(r"\bcollaps\w*\b"),         # collapse, collapsed, ...
]

# --- Category detection. Each pattern is specific to its category; a row that
# matches more than one distinct category is genuinely ambiguous. ---
CATEGORY_PATTERNS = [
    ("Pothole", re.compile(r"\bpot\s?holes?\b")),
    ("Flooding", re.compile(r"\bflood\w*\b")),
    ("Drain Blockage", re.compile(r"\bdrain\w*\b")),
    ("Streetlight", re.compile(
        r"\bstreet\s?lights?\b|\bunlit\b|\bflicker\w*\b|\blights\b"
        r"|\bsubstation\b|\bdarkness\b"
    )),
    ("Waste", re.compile(
        r"\bgarbage\b|\brubbish\b|\bwaste\b|\blitter\b|\btrash\b|\bbins?\b"
        r"|\bdead animal\b|\bcarcass\b|\bdumped\b"
    )),
    ("Noise", re.compile(
        r"\bnoise\b|\bmusic\b|\bloud\b|\bamplifiers?\b|\bhonking\b"
        r"|\bdrilling\b|\bplaying\b|\bidling\b|\bengines\b"
    )),
    ("Road Damage", re.compile(
        r"\broad damage\b|\bcrack(?:ed|s|ing)?\b|\bsink\w*\b|\bsubsid\w*\b"
        r"|\bbuckl\w*\b|\bcollaps\w*\b|\bcrater\b|\bmanhole\b|\bfootpath\b"
        r"|\bpavement\b|\btiles?\b"
    )),
    ("Heat Hazard", re.compile(
        r"\bheat(?:wave)?\b|\bmelting\b|\bbubbling\b|\btemperatures?\b"
        r"|\bburn\w*\b|\bsun\b|\d+\s*°\s*[cf]\b"
    )),
]

# Heritage Damage is only Heritage Damage when a heritage word co-occurs with a
# damage signal; a bare "heritage area/street/zone" mention is just location.
HERITAGE_WORDS = re.compile(r"\bheritage\b|\bmonument\b|\bhistoric\b|\bancient\b")
HERITAGE_DAMAGE_SIGNALS = re.compile(
    r"\bknock(?:ed)?\b|\bbroken\b|\bdefac\w*\b|\bdamag\w*\b|\bnot restored\b"
    r"|\bnot replaced\b|\bremoved\b|\bdismantl\w*\b"
)

# --- Priority support: people/property actively affected -> Standard; pure
# nuisance -> Low. ---
ACTIVE_IMPACT_PATTERNS = re.compile(
    r"\baffect(?:ed|ing|s)?\b|\bstranded\b|\bstuck\b|\bstanding in water\b"
    r"|\binaccessible\b|\bblock(?:ed|ing|s)?\b|\bcommuters?\b"
    r"|\bpassengers?\b|\bpedestrians?\b|\bwalkers?\b|\busers\b"
    r"|\bshoppers?\b|\bresidents?\b|\bcyclists?\b|\belderly\b"
    r"|\bmotorists?\b|\bdrivers?\b|\btraffic\b|\bvehicles?\b|\bpeople\b"
    r"|\brisk\b|\bbus\b|\bmarket\b|\bsafety\b|\bdanger\b|\bhealth\b"
    r"|\bcolony\b|\btraders?\b|\bvisitors?\b|\bincidents?\b"
)

NUISANCE_PATTERNS = re.compile(
    r"\bnuisance\b|\bsmell\b|\bodou?r\b|\bunpleasant\b|\bannoy\w*\b"
    r"|\bweeknights?\b"
)

MISSING_REASON = "No description provided, so the complaint cannot be classified."
UNCLASSIFIABLE_REASON = "The row could not be classified."


def _clean(text: str) -> str:
    return (text or "").strip().lower()


def _snippet(text: str, max_chars: int = 60) -> str:
    return " ".join(text.split())[:max_chars].rstrip(",")


def _is_heritage_damage(desc: str) -> bool:
    return bool(
        HERITAGE_WORDS.search(desc) and HERITAGE_DAMAGE_SIGNALS.search(desc)
    )


def _find_severity(desc: str) -> str:
    for pattern in SEVERITY_PATTERNS:
        match = pattern.search(desc)
        if match:
            return match.group(0)
    return ""


def classify_priority(desc: str) -> str:
    """Urgent on any severity keyword; otherwise Standard if people or
    property are actively affected, or Low for minor/nuisance issues."""
    if _find_severity(desc):
        return "Urgent"
    if ACTIVE_IMPACT_PATTERNS.search(desc):
        return "Standard"
    if NUISANCE_PATTERNS.search(desc):
        return "Low"
    return "Standard"


def classify_category(desc: str):
    """Return (category, flag, reason).

    category is Other and flag is NEEDS_REVIEW when the description alone does
    not point to exactly one category.
    """
    if not desc:
        return "Other", "NEEDS_REVIEW", MISSING_REASON

    matches = []
    if _is_heritage_damage(desc):
        match = HERITAGE_WORDS.search(desc)
        matches.append(("Heritage Damage", match.group(0)))

    for category, pattern in CATEGORY_PATTERNS:
        for match in pattern.finditer(desc):
            matches.append((category, match.group(0)))

    unique = []
    seen = set()
    for category, word in matches:
        if (category, word) not in seen:
            seen.add((category, word))
            unique.append((category, word))

    distinct = {category for category, _ in unique}
    if len(distinct) == 1:
        category = distinct.pop()
        quoted = " and ".join(f"'{word}'" for _, word in unique)
        verb = "points" if len(unique) == 1 else "point"
        return category, "", f"{quoted} {verb} to category {category}."

    if len(distinct) > 1:
        word_a, word_b = unique[0][1], unique[1][1]
        return (
            "Other",
            "NEEDS_REVIEW",
            f"Both '{word_a}' and '{word_b}' appear, so the category is "
            f"genuinely ambiguous.",
        )

    return (
        "Other",
        "NEEDS_REVIEW",
        f"No known category keyword appears in '{_snippet(desc)}'.",
    )


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = _clean(row.get("description") or "")
    complaint_id = str(row.get("complaint_id") or row.get("id") or "").strip()

    category, flag, reason = classify_category(description)
    priority = classify_priority(description)

    if severity := _find_severity(description):
        reason = (
            f"{reason.rstrip('.')}, and severity word '{severity}' requires "
            f"Urgent priority."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV.

    Must: flag nulls, not crash on bad rows, produce output even if some rows
    fail.
    """
    rows = []
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"ERROR: input file not found: {input_path}")
    except Exception as exc:
        print(f"ERROR: could not read input file {input_path}: {exc}")

    results = []
    for index, row in enumerate(rows):
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "complaint_id": str(
                    row.get("complaint_id") or row.get("id") or f"row_{index + 1}"
                ).strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": UNCLASSIFIABLE_REASON,
                "flag": "NEEDS_REVIEW",
            }
        if not result["complaint_id"]:
            result["complaint_id"] = f"row_{index + 1}"
        results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)