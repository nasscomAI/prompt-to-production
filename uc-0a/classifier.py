"""
UC-0A — Complaint Classifier
Implements the classify_complaint and batch_classify skills defined in skills.md,
enforcing every rule from agents.md.
"""
import argparse
import csv
import re
import sys
import logging

# ---------------------------------------------------------------------------
# Constants — sourced directly from agents.md enforcement rules
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that must trigger Urgent (case-insensitive matching)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Pre-compiled regex for severity detection (word-boundary, case-insensitive)
_SEVERITY_RE = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in SEVERITY_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category keyword mapping — maps indicative terms to the canonical category.
# Order matters: more specific patterns are checked first.
# ---------------------------------------------------------------------------

_CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Pothole",        ["pothole"]),
    ("Flooding",       ["flood", "waterlog", "water-log", "submerge", "knee-deep",
                        "waist-deep", "inundat"]),
    ("Streetlight",    ["streetlight", "street light", "street-light", "lamp post",
                        "lamppost", "lights out", "light out", "flickering",
                        "sparking"]),
    ("Drain Blockage", ["drain block", "blocked drain", "clogged drain",
                        "drain clog", "manhole", "sewer block", "sewer overflow"]),
    ("Waste",          ["garbage", "waste", "rubbish", "trash", "dumped",
                        "littering", "overflowing bin", "dead animal",
                        "not removed"]),
    ("Noise",          ["noise", "loud music", "music past midnight",
                        "sound pollution", "honking", "construction noise"]),
    ("Heritage Damage",["heritage"]),
    ("Heat Hazard",    ["heat", "heatwave", "sunstroke", "heat stroke",
                        "temperature"]),
    ("Road Damage",    ["road surface", "road damage", "cracked road", "sinking",
                        "broken road", "road crack", "footpath", "pavement",
                        "broken tiles", "upturned"]),
]


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : A dict representing one CSV row; must contain at least a
            'description' field and a 'complaint_id' field.
    Output: A dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement (agents.md):
      • category  ∈ ALLOWED_CATEGORIES — exact strings only.
      • priority  = Urgent when any severity keyword is present (case-insensitive).
      • reason    = one sentence citing specific words from the description.
      • flag      = NEEDS_REVIEW when category is genuinely ambiguous; blank otherwise.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # --- Error handling (skills.md): empty / unintelligible description ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty or unintelligible.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- 1. Determine category ---------------------------------------------------
    matched_category: str | None = None
    matched_keyword: str | None = None

    for cat, keywords in _CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = cat
                matched_keyword = kw
                break
        if matched_category:
            break

    # If no rule matched → Other + NEEDS_REVIEW
    if matched_category is None:
        matched_category = "Other"

    # --- 2. Determine priority ---------------------------------------------------
    severity_match = _SEVERITY_RE.search(description)
    if severity_match:
        priority = "Urgent"
        severity_word = severity_match.group(1)
    else:
        # Low only for cosmetic/informational with no safety implication
        safety_hints = ["dark", "risk", "danger", "accident", "unsafe",
                        "concern", "stranded", "damage", "blocked",
                        "overflow", "smell", "health"]
        if any(h in desc_lower for h in safety_hints):
            priority = "Standard"
        else:
            priority = "Low"
        severity_word = None

    # --- 3. Build reason (one sentence citing specific words) --------------------
    reason_parts = []
    if matched_keyword and matched_category != "Other":
        reason_parts.append(
            f"Description mentions \"{matched_keyword}\" indicating {matched_category}"
        )
    else:
        reason_parts.append(
            "No clear category keyword found in description"
        )

    if severity_word:
        reason_parts.append(
            f"and contains severity keyword \"{severity_word}\" triggering Urgent priority"
        )
    else:
        reason_parts.append(
            f"with no severity keyword detected so priority is {priority}"
        )

    reason = " ".join(reason_parts) + "."

    # --- 4. Determine flag -------------------------------------------------------
    flag = ""
    if matched_category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row via classify_complaint, write results CSV.

    Error handling (skills.md):
      • Never skip rows silently or halt on a single-row failure.
      • Failed rows → category: Other, priority: Standard,
        reason: "Classification failed — see logs", flag: NEEDS_REVIEW.
      • Preserves input row order.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | row %(message)s",
    )
    logger = logging.getLogger("batch_classify")

    results: list[dict] = []

    # --- Read input CSV ----------------------------------------------------------
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as exc:
        logger.error(f"Failed to read input file {input_path}: {exc}")
        sys.exit(1)

    # --- Classify each row -------------------------------------------------------
    for idx, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:
            logger.warning(f"{idx} — classification failed: {exc}")
            result = {
                "complaint_id": row.get("complaint_id", f"ROW_{idx}"),
                "category": "Other",
                "priority": "Standard",
                "reason": "Classification failed — see logs.",
                "flag": "NEEDS_REVIEW",
            }

        # Merge original row data with classification output
        merged = dict(row)
        merged["category"] = result["category"]
        merged["priority"] = result["priority"]
        merged["reason"] = result["reason"]
        merged["flag"] = result["flag"]
        results.append(merged)

    # --- Write output CSV --------------------------------------------------------
    if not results:
        logger.warning("No rows to write.")
        return

    fieldnames = list(results[0].keys())
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        logger.error(f"Failed to write output file {output_path}: {exc}")
        sys.exit(1)

    logger.info(f"Classified {len(results)} complaints → {output_path}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
