"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import re
import os

# ── Classification Schema ──────────────────────────────────────────────────────

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

# ── Category keyword map (order matters: more specific first) ──────────────────

CATEGORY_RULES = [
    # (category, list-of-trigger-words-or-phrases)
    ("Heritage Damage",  ["heritage", "heritage street", "heritage building", "historic"]),
    ("Heat Hazard",      ["heat hazard", "heat stress", "heat wave", "extreme heat", "temperature"]),
    ("Drain Blockage",   ["drain block", "drain choked", "drain overflow", "blocked drain",
                          "clogged drain", "drain"]),
    ("Flooding",         ["flood", "flooded", "waterlog", "water-log", "knee-deep",
                          "standing water", "inundated", "overflow"]),
    ("Pothole",          ["pothole", "pot-hole", "pot hole", "tyre damage"]),
    ("Streetlight",      ["streetlight", "street light", "lamp", "light out", "lights out",
                          "flickering", "sparking", "electrical"]),
    ("Noise",            ["noise", "music", "loud", "sound", "midnight", "party"]),
    ("Waste",            ["garbage", "waste", "bin", "rubbish", "litter", "dead animal",
                          "dumped", "dump", "sanitation"]),
    ("Road Damage",      ["road", "surface", "crack", "sinking", "manhole", "footpath",
                          "tile", "upturned", "broken road", "road surface"]),
]


def _contains_any(text: str, keywords: list) -> bool:
    """Return True if text contains any keyword (case-insensitive whole-word aware)."""
    text_lower = text.lower()
    for kw in keywords:
        # use word-boundary search for single words, substring for phrases
        if " " in kw:
            if kw in text_lower:
                return True
        else:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return True
    return False


def _determine_category(description: str) -> tuple[str, bool]:
    """
    Returns (category, needs_review).
    needs_review is True when the match is weak or category is Other.
    """
    for category, keywords in CATEGORY_RULES:
        if _contains_any(description, keywords):
            return category, False
    return "Other", True


def _determine_priority(description: str) -> str:
    """Return Urgent / Standard / Low based on severity keywords and description length."""
    if _contains_any(description, SEVERITY_KEYWORDS):
        return "Urgent"
    # Heuristic: longer, detailed descriptions tend to be more impactful → Standard
    if len(description.split()) >= 8:
        return "Standard"
    return "Low"


def _build_reason(description: str, category: str) -> str:
    """
    Build a one-sentence reason that quotes specific words from the description.
    """
    # Extract the most meaningful noun phrase snippet (first clause)
    # Strip to first sentence / clause boundary
    snippet = re.split(r'[.!?;]', description)[0].strip()
    if len(snippet) > 120:
        snippet = snippet[:117] + "..."
    return f"Classified as {category} based on complaint description: \"{snippet}\"."


# ── Public Skills ──────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input keys used: complaint_id, description, location, ward, city
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = (row.get("description") or "").strip()

    # Enforcement: empty description → NEEDS_REVIEW
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided.",
            "flag":         "NEEDS_REVIEW",
        }

    try:
        category, needs_review = _determine_category(description)

        # Contextual boost: check location/ward for school/hospital proximity
        context_text = " ".join([
            row.get("location", ""),
            row.get("ward", ""),
        ])
        full_text = description + " " + context_text

        priority   = _determine_priority(full_text)
        reason     = _build_reason(description, category)
        flag       = "NEEDS_REVIEW" if needs_review else ""

        return {
            "complaint_id": complaint_id,
            "category":     category,
            "priority":     priority,
            "reason":       reason,
            "flag":         flag,
        }

    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] classify_complaint failed for {complaint_id}: {exc}", file=sys.stderr)
        return {
            "complaint_id": complaint_id,
            "category":     "ERROR",
            "priority":     "ERROR",
            "reason":       f"Classification error: {exc}",
            "flag":         "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    - Flags nulls → NEEDS_REVIEW
    - Does not crash on bad rows
    - Produces output even if some rows fail
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results      = []
    total        = 0
    review_count = 0
    error_count  = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            total += 1
            try:
                classification = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] Unexpected error on row {total}: {exc}", file=sys.stderr)
                classification = {
                    "complaint_id": row.get("complaint_id", f"ROW-{total}"),
                    "category":     "ERROR",
                    "priority":     "ERROR",
                    "reason":       f"Unexpected batch error: {exc}",
                    "flag":         "NEEDS_REVIEW",
                }

            # Merge original row + classification (classification fields win on clash)
            merged = {**row, **classification}
            results.append(merged)

            if classification.get("flag") == "NEEDS_REVIEW":
                review_count += 1
                print(
                    f"[REVIEW] {classification['complaint_id']} → "
                    f"{classification['category']} / {classification['priority']}",
                    file=sys.stderr,
                )
            if classification.get("category") == "ERROR":
                error_count += 1

    if not results:
        print("[WARN] No rows found in input file.", file=sys.stderr)
        return

    # Write output — preserve original columns, append classification columns at end
    original_fields       = list(results[0].keys())
    classification_fields = ["category", "priority", "reason", "flag"]
    # Ensure classification fields are at the end, deduplicated
    base_fields = [f for f in original_fields if f not in classification_fields]
    fieldnames  = base_fields + classification_fields

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\n── Batch Summary ──────────────────────────────")
    print(f"  Total rows processed : {total}")
    print(f"  Needs review (flag)  : {review_count}")
    print(f"  Errors               : {error_count}")
    print(f"  Output written to    : {output_path}")
    print(f"───────────────────────────────────────────────\n")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
