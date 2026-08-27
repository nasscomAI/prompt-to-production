"""
UC-0A — Complaint Classifier
Built from agents.md (RICE enforcement) and skills.md skill contracts.
"""
import argparse
import csv
import re
import sys

# ── Classification schema ────────────────────────────────────────────────────

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords → must always trigger priority: Urgent  (agents.md rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword mapping — ordered from most-specific to least-specific.
# Each entry: (category_name, [trigger_keywords])
CATEGORY_RULES = [
    ("Heritage Damage",  ["heritage", "historical", "monument", "ancient", "old city"]),
    ("Drain Blockage",   ["drain", "drainage", "gutter", "sewer", "manhole"]),
    ("Flooding",         ["flood", "flooded", "flooding", "waterlog", "water-log",
                          "inundated", "submerged", "knee-deep", "stranded"]),
    ("Pothole",          ["pothole", "pot-hole", "crater", "tyre damage", "wheel"]),
    ("Streetlight",      ["streetlight", "street light", "lamp post", "light out",
                          "lights out", "flickering", "sparking", "electric", "dark"]),
    ("Noise",            ["noise", "music", "loud", "sound", "midnight", "nighttime"]),
    ("Waste",            ["garbage", "waste", "trash", "litter", "dump", "rubbish",
                          "overflowing", "smell", "dead animal", "decompos"]),
    ("Heat Hazard",      ["heat", "temperature", "sun", "hot", "thermal"]),
    ("Road Damage",      ["road", "surface", "crack", "sinking", "footpath",
                          "pavement", "tile", "broken", "upturned", "damaged road"]),
]


def _extract_keywords(description: str, keyword_list: list[str]) -> list[str]:
    """Return which keywords from keyword_list appear in description (case-insensitive)."""
    text = description.lower()
    return [kw for kw in keyword_list if kw in text]


def _determine_category(description: str) -> tuple[str, bool]:
    """
    Walk CATEGORY_RULES in priority order and return (category, is_ambiguous).
    is_ambiguous is True when no rule matches → falls back to Other.
    """
    text = description.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in text for kw in keywords):
            return category, False
    return "Other", True


def _determine_priority(description: str) -> tuple[str, list[str]]:
    """
    Return (priority, matched_severity_keywords).
    Urgent is mandatory when any severity keyword is present (agents.md rule 2).
    Otherwise default to Standard (Low is reserved for explicit future use).
    """
    matched = _extract_keywords(description, SEVERITY_KEYWORDS)
    if matched:
        return "Urgent", matched
    return "Standard", []


def _build_reason(description: str, category: str, priority: str,
                  severity_words: list[str], is_ambiguous: bool) -> str:
    """
    Build a one-sentence reason that cites specific words from the description
    (agents.md rule 3).
    """
    # Find the first matching category keyword actually present in the description
    category_evidence = ""
    for cat, keywords in CATEGORY_RULES:
        if cat == category:
            found = _extract_keywords(description, keywords)
            if found:
                category_evidence = f'"{found[0]}"'
            break

    if is_ambiguous:
        return (
            f"No clear category keyword found in description; "
            f"classified as Other and flagged for review."
        )

    parts = []
    if category_evidence:
        parts.append(f"Description contains {category_evidence} indicating {category}")
    if severity_words:
        quoted = ", ".join(f'"{w}"' for w in severity_words)
        parts.append(f"severity keyword(s) {quoted} require priority {priority}")

    if parts:
        return "; ".join(parts) + "."
    # Fallback — should not be reached in normal flow
    return f"Classified as {category} with priority {priority} based on description content."


# ── Skill: classify_complaint ────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement (agents.md):
      1. category  — exactly one of the 10 allowed strings.
      2. priority  — Urgent when severity keyword present; Standard otherwise.
      3. reason    — cites specific words from the description.
      4. flag      — NEEDS_REVIEW when category is ambiguous; blank otherwise.
      5. Never hallucinate a sub-category outside the allowed list.
    """
    complaint_id = row.get("complaint_id", "")
    description  = (row.get("description") or "").strip()

    # ── Guard: missing / empty description (skills.md error_handling) ────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description field is missing or empty.",
            "flag":         "NEEDS_REVIEW",
        }

    # ── Core classification ──────────────────────────────────────────────────
    category, is_ambiguous  = _determine_category(description)
    priority, severity_words = _determine_priority(description)
    reason = _build_reason(description, category, priority, severity_words, is_ambiguous)
    flag   = "NEEDS_REVIEW" if is_ambiguous else ""

    # ── Safety assertion: never emit an out-of-schema value (agents.md rule 5) ─
    assert category in ALLOWED_CATEGORIES, f"BUG: illegal category '{category}'"
    assert priority in ALLOWED_PRIORITIES, f"BUG: illegal priority '{priority}'"

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── Skill: batch_classify ────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Continues processing remaining rows even if individual rows fail.
    """
    # ── Read input ───────────────────────────────────────────────────────────
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as exc:
        raise ValueError(f"Could not parse input file '{input_path}': {exc}") from exc

    if not rows:
        raise ValueError(f"Input file '{input_path}' is empty or has no data rows.")

    # ── Classify each row ────────────────────────────────────────────────────
    output_fieldnames = [
        "complaint_id", "description", "category", "priority", "reason", "flag"
    ]
    results = []

    for row in rows:
        complaint_id = row.get("complaint_id", "<unknown>")
        description  = (row.get("description") or "").strip()
        try:
            result = classify_complaint(row)
        except Exception as exc:
            # Do not crash the batch — log and fall back (skills.md error_handling)
            print(
                f"[WARN] complaint_id={complaint_id}: classification error ({exc}); "
                f"falling back to Other/Low/NEEDS_REVIEW",
                file=sys.stderr,
            )
            result = {
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Classification error: {exc}",
                "flag":         "NEEDS_REVIEW",
            }

        # Log NEEDS_REVIEW rows to stderr so they are visible (skills.md error_handling)
        if result["flag"] == "NEEDS_REVIEW":
            print(
                f"[INFO] complaint_id={complaint_id}: flagged NEEDS_REVIEW "
                f"(category={result['category']})",
                file=sys.stderr,
            )

        result["description"] = description
        results.append({k: result.get(k, "") for k in output_fieldnames})

    # ── Write output ─────────────────────────────────────────────────────────
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
