"""
UC-0A — Complaint Classifier
Classifies municipal complaints into categories and priority levels
based on agents.md enforcement rules and skills.md specifications.
"""
import argparse
import csv
import re
import sys

# ---------------------------------------------------------------------------
# Allowed categories (agents.md enforcement rule 1)
# ---------------------------------------------------------------------------
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}

# ---------------------------------------------------------------------------
# Severity keywords → force Urgent (agents.md enforcement rule 3)
# ---------------------------------------------------------------------------
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
}

# ---------------------------------------------------------------------------
# Category keyword map — longest-match-first tokens mapped to categories.
# Order matters: more specific phrases come before generic ones.
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: list[tuple[list[str], str]] = [
    # Drain Blockage (before Flooding so "drain" is not swallowed)
    (["drain", "blocked drain", "drainage", "clogged drain", "nullah", "nala",
      "manhole overflow", "sewer", "sewage"], "Drain Blockage"),
    # Flooding
    (["flood", "flooding", "waterlog", "waterlogging", "submerged",
      "inundated", "water stagnation", "water logging"], "Flooding"),
    # Heritage Damage
    (["heritage", "monument", "historic", "historical", "archaeological",
      "ancient", "temple damage", "fort damage"], "Heritage Damage"),
    # Heat Hazard
    (["heat", "heatwave", "heat wave", "sunstroke", "heat stroke",
      "overheating", "hot road", "melting road", "tar melting"], "Heat Hazard"),
    # Road Damage (before Pothole so "road crack" is not missed)
    (["road damage", "road crack", "road cave", "road broken", "road sinking",
      "road erosion", "damaged road", "broken road", "cracked road",
      "cave-in", "road subsidence"], "Road Damage"),
    # Pothole
    (["pothole", "pot hole", "pit on road", "crater", "hole in road",
      "road pit", "dip in road"], "Pothole"),
    # Streetlight
    (["streetlight", "street light", "lamp post", "lamppost", "light pole",
      "pole light", "bulb not working", "dark street", "no light",
      "broken light", "light out"], "Streetlight"),
    # Waste
    (["waste", "garbage", "trash", "rubbish", "litter", "dumping",
      "dump", "debris", "filth", "dirty", "sanitation",
      "dustbin", "overflowing bin"], "Waste"),
    # Noise
    (["noise", "loud", "loudness", "loudspeaker", "honking", "horn",
      "construction noise", "music", "disturbance", "sound pollution",
      "noise pollution"], "Noise"),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Detect the best-fit category from the description text.
    Returns (category, is_ambiguous).
    """
    desc_lower = description.lower()

    matched_categories: list[str] = []
    for keywords, category in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc_lower:
                if category not in matched_categories:
                    matched_categories.append(category)
                break  # one keyword match per group is enough

    if len(matched_categories) == 0:
        return "Other", True  # no match → ambiguous
    if len(matched_categories) == 1:
        return matched_categories[0], False
    # Multiple categories matched → ambiguous (agents.md rule 6)
    return "Other", True


def _detect_priority(description: str) -> str:
    """
    Detect priority based on severity keywords (agents.md enforcement rule 3).
    """
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        # Use word-boundary matching to avoid false positives
        if re.search(rf"\b{re.escape(kw)}\b", desc_lower):
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    # Extract the first few meaningful words from the description for citation
    words = description.split()
    cited = " ".join(words[:12]) if len(words) > 12 else description
    cited = cited.strip().rstrip(".")

    if priority == "Urgent":
        # Find which severity keyword triggered Urgent
        desc_lower = description.lower()
        trigger = None
        for kw in SEVERITY_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", desc_lower):
                trigger = kw
                break
        return (
            f"Classified as {category} (Urgent) because the description "
            f"\"{cited}\" contains the severity keyword '{trigger}'."
        )
    return (
        f"Classified as {category} ({priority}) based on the description "
        f"\"{cited}\"."
    )


# ── public API ────────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Parameters
    ----------
    row : dict
        Must contain at minimum a 'description' field (string).

    Returns
    -------
    dict with keys: category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", None)

    # ── Handle empty / null / nonsensical descriptions (enforcement rule 7) ──
    if not description or not isinstance(description, str) or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or not a valid civic complaint.",
            "flag": "NEEDS_REVIEW",
        }

    description = description.strip()

    # ── Detect category ──
    category, is_ambiguous = _detect_category(description)

    # ── Detect priority ──
    priority = _detect_priority(description)

    # If no severity keywords and category is clear → Standard
    # For minor/cosmetic → Low (heuristic: very short descriptions)
    if priority != "Urgent" and len(description.split()) <= 4:
        priority = "Low"

    # ── Build reason ──
    reason = _build_reason(description, category, priority)

    # ── Flag ──
    flag = "NEEDS_REVIEW" if is_ambiguous or category == "Other" else ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    - Flags nulls/empty descriptions with NEEDS_REVIEW.
    - Does not crash on bad rows; writes error rows with safe defaults.
    - Produces output even if some rows fail.

    Parameters
    ----------
    input_path : str   Path to the input complaints CSV.
    output_path : str  Path to write the classified results CSV.
    """
    # ── Validate input file ──
    try:
        infile = open(input_path, "r", newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: '{input_path}'. Please provide a valid CSV path."
        )
    except Exception as exc:
        raise RuntimeError(
            f"Cannot read input file '{input_path}': {exc}"
        )

    results: list[dict] = []
    classification_fields = ["category", "priority", "reason", "flag"]
    original_fieldnames: list[str] = []

    with infile:
        reader = csv.DictReader(infile)
        original_fieldnames = list(reader.fieldnames) if reader.fieldnames else []

        for row_num, row in enumerate(reader, start=2):  # row 1 is header
            try:
                result = classify_complaint(row)
                # Merge original columns with classification output
                out_row = dict(row)
                out_row.update(result)
                results.append(out_row)
            except Exception as exc:
                # Do not skip — write with safe defaults (skills.md error handling)
                out_row = dict(row)
                out_row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed on row {row_num}: {exc}",
                    "flag": "NEEDS_REVIEW",
                })
                results.append(out_row)
                print(
                    f"[WARN] Row {row_num} classification failed: {exc}",
                    file=sys.stderr,
                )

    # ── Determine output fieldnames ──
    # Original columns + classification fields (avoid duplicates)
    out_fields = list(original_fieldnames)
    for f in classification_fields:
        if f not in out_fields:
            out_fields.append(f)
    # Ensure complaint_id is present
    if "complaint_id" not in out_fields:
        out_fields.insert(0, "complaint_id")

    # ── Write output CSV ──
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
