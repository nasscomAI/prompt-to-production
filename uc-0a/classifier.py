"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md and skills from skills.md.
"""
import argparse
import csv
import os
import re
import sys

# ---------------------------------------------------------------------------
# Schema — agents.md enforcement references these exact strings
# ---------------------------------------------------------------------------

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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
}

OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]

# ---------------------------------------------------------------------------
# Category keyword mapping (used by the heuristic classifier)
# ---------------------------------------------------------------------------

CATEGORY_PATTERNS = [
    ("Pothole",        r"\bpothole|pot\s*hole|crater|pit\s*on\s*road\b"),
    ("Flooding",       r"\bflood|waterlog|inundat|standing\s*water|overflow\b"),
    ("Streetlight",    r"\bstreet\s*light|streetlight|lamp\s*post|light\s*out|dark\s*street\b"),
    ("Waste",          r"\bgarbage|trash|waste|rubbish|litter|dumping|dump\b"),
    ("Noise",          r"\bnoise|loud|sound|music|blaring|honking\b"),
    ("Road Damage",    r"\broad\s*damage|broken\s*road|cracked\s*road|road\s*crack|asphalt|pavement\b"),
    ("Heritage Damage",r"\bheritage|monument|historic|ancient|old\s*building|heritage\s*site\b"),
    ("Heat Hazard",    r"\bheat|temperature|hot\s*road|burning|thermal\b"),
    ("Drain Blockage", r"\bdrain|sewer|blocked\s*drain|gutter|manhole|sewage\b"),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Return (category, is_ambiguous).
    Tries each pattern in order. If no pattern matches, returns ("Other", False).
    If multiple patterns match, returns the first match and marks ambiguous.
    """
    text = description.lower()
    matches = []
    for cat, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, text):
            matches.append(cat)

    if len(matches) == 0:
        return "Other", False
    if len(matches) == 1:
        return matches[0], False
    # Multiple matches — use first but flag ambiguity
    return matches[0], True


def _detect_priority(description: str) -> str:
    """
    Return Urgent if any severity keyword is present, else Standard.
    Low is reserved for rows with very minimal/non-actionable descriptions.
    """
    text = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return "Urgent"
    # Minimal descriptions (fewer than 4 words) get Low
    if len(description.split()) < 4:
        return "Low"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason that cites specific words from the description.
    """
    desc_strip = description.strip()
    # Find the specific triggering words to cite
    cited_words = []

    # Cite severity keyword if Urgent
    if priority == "Urgent":
        text_lower = desc_strip.lower()
        for kw in SEVERITY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                cited_words.append(f'"{kw}"')
                break

    # Cite the first matching category keyword
    for cat, pattern in CATEGORY_PATTERNS:
        if cat == category:
            m = re.search(pattern, desc_strip, re.IGNORECASE)
            if m:
                cited_words.append(f'"{m.group(0)}"')
            break

    if cited_words:
        cited = " and ".join(cited_words)
        return (
            f'Classified as {category} with {priority} priority '
            f'based on the term(s) {cited} in the description.'
        )

    # Fallback: quote first meaningful phrase from description (up to 8 words)
    words = desc_strip.split()
    snippet = " ".join(words[:8]) + ("..." if len(words) > 8 else "")
    return (
        f'Classified as {category} with {priority} priority '
        f'based on the description: "{snippet}".'
    )


# ---------------------------------------------------------------------------
# Skill 1 — classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : dict with at minimum a 'description' key (string).
    Output: dict with keys — category, priority, reason, flag.

    Implements all RICE enforcement rules and skill error_handling from
    agents.md / skills.md.
    """
    description = row.get("description", "").strip()

    # --- error_handling: missing_description ---
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description field is empty or missing — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    # --- Core classification ---
    try:
        category, is_ambiguous = _detect_category(description)
        priority = _detect_priority(description)
        reason = _build_reason(description, category, priority)

        # --- error_handling: hallucinated_category guard ---
        if category not in ALLOWED_CATEGORIES:
            category = "Other"
            is_ambiguous = True

        # --- error_handling: false_confidence guard ---
        flag = "NEEDS_REVIEW" if is_ambiguous else ""

        # --- Enforcement: reason must be grounded ---
        if not reason or len(reason.strip()) == 0:
            reason = "Insufficient description detail to justify classification."
            flag = "NEEDS_REVIEW"

        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    except Exception as exc:
        # --- error_handling: classify_complaint_failure ---
        return {
            "category": "Other",
            "priority": "Low",
            "reason": str(exc),
            "flag": "NEEDS_REVIEW",
        }


# ---------------------------------------------------------------------------
# Skill 2 — batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read city input CSV, apply classify_complaint per row, write results CSV.

    Implements all skill error_handling rules from skills.md.
    """

    # --- error_handling: file_not_found ---
    if not os.path.exists(input_path):
        sys.exit(
            f"[ERROR] Input file not found: {input_path}\n"
            "No processing was performed."
        )

    # --- error_handling: output_directory_missing ---
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Read all rows first so we can validate count before writing
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        input_rows = list(reader)

    # --- error_handling: empty_input_file ---
    if not input_rows:
        sys.exit(
            f"[ERROR] Input file contains no data rows: {input_path}\n"
            "No output file was written."
        )

    results = []
    failed_indices = []

    for idx, row in enumerate(input_rows):
        result = classify_complaint(row)

        # Carry through any identifier columns present in the source row
        # (e.g. complaint_id, location) but never category/priority_flag
        passthrough = {
            k: v for k, v in row.items()
            if k.lower() not in {"category", "priority_flag"}
        }
        combined = {**passthrough, **result}

        # Guard: if classify_complaint returned a flag, record the index
        if result.get("flag") == "NEEDS_REVIEW":
            failed_indices.append(idx)

        results.append(combined)

    # --- error_handling: row_count_mismatch ---
    if len(results) != len(input_rows):
        sys.exit(
            f"[ERROR] Row count mismatch: read {len(input_rows)} rows "
            f"but produced {len(results)} results. Output not written."
        )

    # --- error_handling: taxonomy_drift ---
    # Validate that identical description patterns received identical categories.
    # We do a lightweight check: scan for pairs where description keywords
    # strongly suggest the same complaint type but categories differ.
    _check_taxonomy_drift(results)

    # Write output
    if not results:
        sys.exit("[ERROR] No results to write.")

    fieldnames = list(results[0].keys())
    # Ensure the four required output fields are always present
    for field in OUTPUT_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    # Summary
    needs_review = sum(1 for r in results if r.get("flag") == "NEEDS_REVIEW")
    print(f"  Rows processed : {len(results)}")
    print(f"  NEEDS_REVIEW   : {needs_review}")
    if needs_review:
        print(f"  Review indices : {failed_indices}")


def _check_taxonomy_drift(results: list[dict]) -> None:
    """
    Detect and warn about taxonomy drift.
    Groups rows by dominant category keyword and checks for category inconsistency.
    Logs a warning (does not abort) if drift is found, per skills.md.
    """
    # Build a simple fingerprint → category map
    seen: dict[str, set] = {}
    for row in results:
        desc = row.get("description", "").lower()
        cat = row.get("category", "")
        for label, pattern in CATEGORY_PATTERNS:
            if re.search(pattern, desc):
                seen.setdefault(label, set()).add(cat)

    drifted = {label: cats for label, cats in seen.items() if len(cats) > 1}
    if drifted:
        print("[WARNING] Taxonomy drift detected:")
        for label, cats in drifted.items():
            print(f"  Pattern '{label}' mapped to multiple categories: {cats}")
        print("  Review NEEDS_REVIEW rows and re-run if necessary.")


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