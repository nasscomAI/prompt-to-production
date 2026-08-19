"""
UC-0A — Complaint Classifier
Nasscom AI Code Sarathi — Prompt-to-Production Workshop

CRAFT Cycle: Create → Review → Audit → Fix → Test
Participant: Achyuth | City: Hyderabad

Design philosophy (from workshop):
  - Prevent hallucinations     : category locked to exact taxonomy
  - Prevent silent failures    : every row gets an output, errors are flagged
  - Prevent unsupported assumptions : only description text is used
  - Prevent incorrect calculations  : priority override is rule-based, not inferred
  - Enforce traceability       : reason field cites specific description words
  - Enforce explainability     : flag=NEEDS_REVIEW surfaces ambiguity to humans
"""

import argparse
import csv
import logging
import os
import sys
from typing import Tuple

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("uc-0a")

# ---------------------------------------------------------------------------
# Schema constants  (enforcement layer — agents.md rules reflected here)
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

# Severity keywords that MUST trigger Urgent priority (agents.md enforcement rule 2)
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# ---------------------------------------------------------------------------
# Category keyword mapping — ordered from most specific to least specific.
# Each entry: (category_name, set_of_trigger_keywords)
# First match wins. "Other" is the final fallback.
# ---------------------------------------------------------------------------
CATEGORY_RULES = [
    # Heritage Damage — before Road Damage to catch "heritage zone" descriptions
    ("Heritage Damage",  {"heritage", "monument", "heritage zone", "historic", "charminar",
                           "fort", "old city", "archaeological"}),
    # Flooding
    ("Flooding",         {"flood", "flooded", "flooding", "inundated", "waterlogged",
                           "submerged", "water logging", "under water"}),
    # Drain Blockage — overlaps with flooding; check description for "drain"
    ("Drain Blockage",   {"drain blocked", "drain blockage", "blocked drain",
                           "drain overflow", "stormwater drain", "drainage blocked",
                           "clogged drain", "mosquito breeding", "dengue"}),
    # Pothole
    ("Pothole",          {"pothole", "pot hole", "pot-hole"}),
    # Road Damage — broader than pothole
    ("Road Damage",      {"road collapsed", "road collapse", "crater", "road damage",
                           "road broken", "road sunk", "cave", "caved", "sinkhole"}),
    # Waste
    ("Waste",            {"garbage", "waste", "trash", "rubbish", "litter", "dumping",
                           "not cleared", "refuse", "filth"}),
    # Noise
    ("Noise",            {"noise", "drilling", "loud", "sound", "horn", "music",
                           "idling", "engine", "truck", "generator"}),
    # Streetlight
    ("Streetlight",      {"streetlight", "street light", "light not working", "lamp post",
                           "dark road", "no lighting", "bulb", "light off"}),
    # Heat Hazard
    ("Heat Hazard",      {"heat", "temperature", "hot", "fire hydrant", "sun",
                           "heat wave", "heat stroke"}),
]


# ---------------------------------------------------------------------------
# Core classification function
# ---------------------------------------------------------------------------

def _extract_category(description_lower: str) -> Tuple[str, bool]:
    """
    Return (category, is_ambiguous).
    is_ambiguous is True when two or more category rules match.
    """
    matched = []
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in description_lower:
                matched.append(cat_name)
                break  # only count each category once

    if len(matched) == 0:
        return "Other", False
    if len(matched) == 1:
        return matched[0], False
    # Multiple matches — dominant signal is the first match (most-specific rule wins)
    return matched[0], True


def _extract_priority(description_lower: str) -> str:
    """
    Returns Urgent | Standard | Low.
    Severity keywords unconditionally trigger Urgent (agents.md enforcement rule 2).
    """
    for kw in SEVERITY_KEYWORDS:
        if kw in description_lower:
            return "Urgent"
    # Heuristic: if days_open info suggests active infrastructure risk → Standard
    # (We only use description here; days_open is metadata, not description text.)
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build an evidence-based reason sentence by citing words from the description.
    Avoids generic boilerplate (workshop anti-pattern).
    """
    desc_lower = description.lower()

    # Find which keywords triggered the category
    cat_evidence = []
    for cat_name, keywords in CATEGORY_RULES:
        if cat_name == category:
            for kw in keywords:
                if kw in desc_lower:
                    cat_evidence.append(f'"{kw}"')
            break

    # Find which keyword triggered Urgent (if applicable)
    priority_evidence = []
    if priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if kw in desc_lower:
                priority_evidence.append(f'"{kw}"')

    # Compose reason
    parts = []
    if cat_evidence:
        parts.append(f"Description contains {', '.join(cat_evidence[:2])}, indicating {category}")
    else:
        # Category was Other — no keyword matched
        parts.append(f"No specific category keyword matched; classified as {category}")

    if priority_evidence:
        parts.append(
            f"severity keyword {priority_evidence[0]} present, triggering Urgent priority"
        )

    return "; ".join(parts) + "."


def _validate_output(row: dict) -> list:
    """
    Returns list of validation error strings (empty list = valid).
    Implements post-classification guardrails from skills.md.
    """
    errors = []
    if row.get("category") not in ALLOWED_CATEGORIES:
        errors.append(f"Invalid category: {row.get('category')!r}")
    if row.get("priority") not in ALLOWED_PRIORITIES:
        errors.append(f"Invalid priority: {row.get('priority')!r}")
    if not row.get("reason"):
        errors.append("Reason is empty")
    if row.get("flag") not in {"NEEDS_REVIEW", ""}:
        errors.append(f"Invalid flag: {row.get('flag')!r}")
    return errors


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict — must contain 'description'; 'complaint_id' is used if present.
    Output: dict with keys: complaint_id, category, priority, reason, flag.

    Guarantees (from skills.md):
      - Never raises an exception to the caller.
      - Output always passes schema validation.
      - Reason always cites words from the description.
    """
    complaint_id = str(row.get("complaint_id", "UNKNOWN")).strip() or "UNKNOWN"

    # Coerce description to string safely
    raw_desc = row.get("description", "")
    try:
        description = str(raw_desc).strip()
    except Exception:
        description = ""

    # --- Guard: empty or unreadable description ---
    if not description or len(description.split()) < 2:
        log.warning("Row %s: description is empty or too short — flagging NEEDS_REVIEW", complaint_id)
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description was empty or unreadable.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Step 1: Determine category ---
    category, is_ambiguous = _extract_category(desc_lower)

    # --- Step 2: Determine priority (severity keyword override is inside _extract_priority) ---
    priority = _extract_priority(desc_lower)

    # Special case: "Other" category with no severity keyword → Low priority
    if category == "Other" and priority == "Standard":
        priority = "Low"

    # --- Step 3: Build evidence-based reason ---
    reason = _build_reason(description, category, priority)

    # --- Step 4: Set flag ---
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    result = {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }

    # --- Step 5: Post-classification validation (guardrail) ---
    errors = _validate_output(result)
    if errors:
        log.error(
            "Row %s failed schema validation: %s — applying safe defaults",
            complaint_id, errors
        )
        result.update({
            "category": "Other",
            "priority": "Low",
            "flag":     "NEEDS_REVIEW",
            "reason":   f"Schema validation failed ({'; '.join(errors)}); safe defaults applied.",
        })

    log.info(
        "Row %-12s → category=%-16s priority=%-8s flag=%s",
        complaint_id, result["category"], result["priority"], result["flag"] or "(none)",
    )
    return result


# ---------------------------------------------------------------------------
# Batch processing function
# ---------------------------------------------------------------------------

OUTPUT_FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]

SAFE_DEFAULTS = {
    "category": "Other",
    "priority": "Low",
    "reason":   "Row-level exception during classification; safe defaults applied.",
    "flag":     "NEEDS_REVIEW",
}


def batch_classify(input_path: str, output_path: str) -> Tuple[int, int]:
    """
    Read input CSV, classify each row, write results CSV.

    Returns: (total_rows_processed, error_rows_count)
    Raises:  FileNotFoundError if input_path does not exist.
             ValueError if the 'description' column is missing.
             PermissionError if output_path is not writable.
    """
    # --- Input validation ---
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path!r}")

    if os.path.exists(output_path):
        log.warning("Output file %r already exists — will overwrite.", output_path)

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    total = 0
    errors = 0

    # Try UTF-8 first, fall back to latin-1
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(input_path, newline="", encoding=encoding) as infile:
                reader = csv.DictReader(infile)

                # Validate required column
                if reader.fieldnames is None or "description" not in reader.fieldnames:
                    raise ValueError(
                        f"Input CSV is missing required column 'description'. "
                        f"Found columns: {reader.fieldnames}"
                    )

                with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDNAMES)
                    writer.writeheader()

                    for line_num, row in enumerate(reader, start=2):  # line 1 is header
                        # Skip blank rows
                        if not any(v.strip() for v in row.values() if v):
                            log.warning("Line %d: blank row — skipped.", line_num)
                            continue

                        try:
                            result = classify_complaint(row)
                        except Exception as exc:  # noqa: BLE001 — intentional catch-all
                            complaint_id = str(row.get("complaint_id", f"LINE_{line_num}"))
                            log.error(
                                "Line %d (id=%s): unexpected error — %s",
                                line_num, complaint_id, exc
                            )
                            result = {"complaint_id": complaint_id, **SAFE_DEFAULTS}
                            errors += 1

                        # Guardrail: reject "None" / "nan" values before writing
                        for key in OUTPUT_FIELDNAMES:
                            val = str(result.get(key, ""))
                            if val.lower() in {"none", "nan", "null"}:
                                log.warning(
                                    "Row %s field %r had value %r — replaced with empty string.",
                                    result.get("complaint_id"), key, val
                                )
                                result[key] = ""

                        writer.writerow({k: result.get(k, "") for k in OUTPUT_FIELDNAMES})
                        total += 1

            break  # encoding worked
        except UnicodeDecodeError:
            if encoding == "latin-1":
                raise  # both encodings failed
            log.warning("UTF-8 decode failed — retrying with latin-1.")

    log.info("Batch complete: %d rows processed, %d errors.", total, errors)
    return total, errors


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — Nasscom AI Code Sarathi"
    )
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        total, err = batch_classify(args.input, args.output)
        print(f"Done. {total} rows written to {args.output!r}  ({err} errors flagged).")
        sys.exit(0)
    except (FileNotFoundError, ValueError, PermissionError) as exc:
        log.error("Fatal: %s", exc)
        sys.exit(1)
