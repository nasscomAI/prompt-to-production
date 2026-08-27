"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in agents.md and skills.md.
"""
import argparse
import csv
import re
import sys

# ── agents.md › enforcement[0]: exact category allowlist ─────────────────────
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# ── agents.md › enforcement[1]: severity keywords that force Urgent ───────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Rule-based keyword map for category assignment ────────────────────────────
# Maps a category to the keywords that signal it (checked in order; first match wins)
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "crater", "pit in road"]),
    ("Flooding",        ["flood", "waterlog", "submerged", "inundated", "water on road"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "light out", "dark road", "no light", "unlit"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter", "dumping", "sewage smell"]),
    ("Noise",           ["noise", "loud", "sound", "honking", "blaring", "disturbance", "music"]),
    ("Road Damage",     ["road damage", "broken road", "road crack", "damaged road", "road broken", "road surface", "paving"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "old building"]),
    ("Heat Hazard",     ["heat", "hot", "temperature", "sun", "thermal", "heat wave", "melting"]),
    ("Drain Blockage",  ["drain", "blocked drain", "clogged", "overflow", "manhole", "sewer"]),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Return (category, is_ambiguous).
    Scans description against CATEGORY_KEYWORDS; first match wins.
    If no keyword matches → Other + ambiguous flag.
    """
    text = description.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    if len(matched) > 1:
        # Multiple categories signal ambiguity — pick first but flag
        return matched[0], True
    # No match → Other + NEEDS_REVIEW (agents.md enforcement[3])
    return "Other", True


def _detect_priority(description: str) -> str:
    """
    Return Urgent if any severity keyword is present (case-insensitive),
    otherwise Standard. Low is reserved for explicit caller override.
    agents.md › enforcement[1]
    """
    text = description.lower()
    if any(kw in text for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason that quotes specific words from the description.
    agents.md › enforcement[2]
    """
    # Find the first matching severity keyword to quote, if any
    text_lower = description.lower()
    quoted_kw = next((kw for kw in SEVERITY_KEYWORDS if kw in text_lower), None)

    # Find up to the first 8 words of the description as a quote anchor
    snippet = " ".join(description.split()[:8]).rstrip(".,;")

    if quoted_kw and priority == "Urgent":
        return (
            f'Classified as {category} with Urgent priority because the description '
            f'contains "{quoted_kw}" in: "{snippet}...".'
        )
    return (
        f'Classified as {category} with {priority} priority based on description: '
        f'"{snippet}...".'
    )


# ── skill: classify_complaint ─────────────────────────────────────────────────
def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input  (skills.md): dict with at least 'description'; may include
                         'complaint_id' and other passthrough fields.
    Output (skills.md): dict with keys complaint_id, category, priority,
                         reason, flag.

    Error handling (skills.md):
    - Empty / missing description → Other, Low, NEEDS_REVIEW.
    - Severity keyword present but category ambiguous → Urgent, NEEDS_REVIEW.
    - agents.md enforcement[3]: never guess; use Other + NEEDS_REVIEW.
    """
    complaint_id = row.get("complaint_id", "")
    description  = (row.get("description") or "").strip()

    # Empty description (skills.md error_handling)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description field was empty.",
            "flag":         "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)

    # Severity keyword present but ambiguous → keep Urgent, add NEEDS_REVIEW
    if is_ambiguous and priority == "Urgent":
        flag = "NEEDS_REVIEW"
    elif is_ambiguous:
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    reason = _build_reason(description, category, priority)

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── skill: batch_classify ─────────────────────────────────────────────────────
def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.

    Input  (skills.md): path to test_[city].csv; must have a 'description' column.
    Output (skills.md): results_[city].csv — all original columns + 4 appended fields.

    Error handling (skills.md):
    - NEEDS_REVIEW rows are written through, not skipped.
    - Rows with missing description get safe defaults.
    - File I/O errors surface immediately with path + row index; processing halts.
    """
    RESULT_FIELDS = ["category", "priority", "reason", "flag"]

    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                print(f"ERROR: {input_path} appears to be empty.", file=sys.stderr)
                sys.exit(1)

            out_fieldnames = list(reader.fieldnames) + RESULT_FIELDS

            try:
                with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                    writer.writeheader()

                    for row_idx, row in enumerate(reader, start=2):  # 2 = first data row
                        try:
                            result = classify_complaint(row)
                        except Exception as exc:
                            # Individual row failure — write safe fallback, continue
                            print(
                                f"WARNING: row {row_idx} classification failed "
                                f"({exc}); writing NEEDS_REVIEW fallback.",
                                file=sys.stderr,
                            )
                            result = {
                                "complaint_id": row.get("complaint_id", ""),
                                "category":     "Other",
                                "priority":     "Low",
                                "reason":       f"Classification error at row {row_idx}.",
                                "flag":         "NEEDS_REVIEW",
                            }

                        # Merge original row with classification results
                        out_row = dict(row)
                        for field in RESULT_FIELDS:
                            out_row[field] = result.get(field, "")
                        writer.writerow(out_row)

            except OSError as exc:
                print(f"ERROR writing to {output_path}: {exc}", file=sys.stderr)
                sys.exit(1)

    except OSError as exc:
        print(f"ERROR reading {input_path}: {exc}", file=sys.stderr)
        sys.exit(1)


# ── CLI entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
