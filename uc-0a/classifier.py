"""
UC-0A — Complaint Classifier
Implemented using the RICE prompt in agents.md and the skill contracts in skills.md.
"""
import argparse
import csv
import sys

# ---------------------------------------------------------------------------
# Classification schema — exact strings required by agents.md enforcement rule 1
# ---------------------------------------------------------------------------
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

# agents.md enforcement rule 2 — severity keywords that must trigger Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (order matters: more specific phrases first)
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "crater", "hole in the road", "hole in road"]),
    ("Flooding",        ["flood", "flooding", "waterlog", "inundat", "standing water", "submerged", "water logging"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "lamppost", "light not working",
                         "no light", "dark street", "lighting", "light out"]),
    ("Waste",           ["garbage", "waste", "trash", "litter", "rubbish", "dump", "refuse",
                         "overflowing bin", "bin overflow", "solid waste"]),
    ("Noise",           ["noise", "loud", "blaring", "honking", "sound pollution", "construction noise",
                         "night noise", "nuisance sound"]),
    ("Road Damage",     ["road damage", "broken road", "cracked road", "road crack", "road broken",
                         "tar", "asphalt", "damaged road", "road surface"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "temple damage",
                         "heritage site", "heritage structure"]),
    ("Heat Hazard",     ["heat", "hot surface", "heat wave", "scorching", "overheating",
                         "heat hazard", "burning surface"]),
    ("Drain Blockage",  ["drain", "blocked drain", "sewer", "manhole", "drainage", "clog",
                         "blocked gutter", "overflowing drain"]),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_category(description: str) -> tuple[str, str]:
    """
    Return (category, matched_phrase) using keyword matching.
    Falls back to ("Other", "") if nothing matches.
    """
    lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in lower:
                return category, kw
    return "Other", ""


def _detect_priority(description: str) -> tuple[str, str]:
    """
    Return (priority, matched_keyword).
    Priority is Urgent iff a severity keyword is present (agents.md rule 2).
    """
    lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in lower:
            return "Urgent", kw
    return "Standard", ""


def _build_reason(description: str, category: str, priority: str,
                  cat_phrase: str, sev_keyword: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description
    (agents.md enforcement rule 3).
    """
    parts = []
    if cat_phrase:
        parts.append(f'"{cat_phrase}" indicates {category}')
    else:
        parts.append(f"no clear category keyword found — classified as {category}")
    if priority == "Urgent" and sev_keyword:
        parts.append(f'"{sev_keyword}" triggers Urgent priority')
    return "; ".join(parts) + "."


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict with at least a 'description' key (and optionally 'complaint_id').
    Output: dict with keys: complaint_id, category, priority, reason, flag.

    Follows agents.md enforcement rules 1–4 and the skill contract in skills.md.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""

    # Enforcement rule 4 / skills.md error_handling: empty description → fallback
    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description was empty or missing — cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    category, cat_phrase   = _detect_category(description)
    priority, sev_keyword  = _detect_priority(description)
    reason                 = _build_reason(description, category, priority,
                                           cat_phrase, sev_keyword)

    # Enforcement rule 4: set NEEDS_REVIEW when category falls back to Other
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row with classify_complaint, write results CSV.

    - Row-level failures are caught; a NEEDS_REVIEW fallback row is written and
      processing continues (skills.md error_handling).
    - FileNotFoundError is raised (not swallowed) if input_path does not exist.
    - All errors per row are logged to stderr.
    """
    OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        in_file = open(input_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}\n"
            "Check the path and try again."
        )

    with in_file, open(output_path, "w", newline="", encoding="utf-8") as out_file:
        reader = csv.DictReader(in_file)
        writer = csv.DictWriter(out_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            complaint_id = row.get("complaint_id", f"row-{i}")
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as exc:
                print(
                    f"[WARN] Row {i} (complaint_id={complaint_id}) failed: {exc}",
                    file=sys.stderr,
                )
                writer.writerow({
                    "complaint_id": complaint_id,
                    "category":     "Other",
                    "priority":     "Low",
                    "reason":       f"Row-level error during classification: {exc}",
                    "flag":         "NEEDS_REVIEW",
                })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
