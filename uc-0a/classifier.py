"""
UC-0A — Complaint Classifier
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.

Fixes applied over the naive baseline (see git history for the naive
Control-step run and its failures):
  1. Taxonomy drift    -> category restricted to a fixed enum, checked in a
                           deterministic keyword-priority order.
  2. Severity blindness -> severity keywords are checked FIRST, before any
                           category/days_open logic, and force Urgent.
  3. Missing reason     -> every row gets a reason quoting the matched text.
  4. False confidence   -> ambiguous / no-match rows fall back to
                           category=Other, flag=NEEDS_REVIEW instead of
                           guessing.
  5. Crash safety       -> per-row try/except so one bad row can't blow up
                           the whole batch.

See agents.md for the enforcement rules this file implements and skills.md
for the two skills (classify_complaint, batch_classify) this file defines.
"""
import argparse
import csv
import re

# ---------------------------------------------------------------------------
# Fixed taxonomy (agents.md enforcement rule #1) — exact strings only.
# ---------------------------------------------------------------------------
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that must force Urgent (agents.md enforcement rule #2).
SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "hospitalised", "hospitalized", "ambulance", "fire", "hazard",
    "fell", "collapse", "collapsed",
]

# Category keyword groups, checked in this priority order. Order matters:
# more specific / higher-severity categories are checked before generic
# ones so a row like "underpass flooded, drain completely blocked" lands on
# Flooding (the actual symptom) rather than Drain Blockage (the cause), and
# a row with an explicit heat reading lands on Heat Hazard before Road
# Damage even though it also describes road surface.
CATEGORY_RULES = [
    ("Heat Hazard", [
        r"\bheat\b", r"heatwave", r"melt", r"\bburns?\b", r"scorching",
        r"sunstroke", r"unbearable", r"dangerous temperatur", r"°c", r"\bc\b°",
        r"\d{2,3}\s*°",
    ]),
    # Checked early and narrowly (requires BOTH a heritage/historic word AND
    # a damage verb, in either order) because it is the most specific rule:
    # e.g. "heritage lamp post knocked over" must win over the generic
    # Streetlight rule below, not lose to it just because "lamp post" also
    # appears later in CATEGORY_RULES.
    ("Heritage Damage", [
        r"heritage.*(damag|defac|broken|knock|not replaced|not restored|removed)",
        r"(damag|defac|broken|knock|not replaced|not restored).*heritage",
        r"historic.*(broken|damag|defac)",
        r"(broken|damag|defac).*historic",
    ]),
    ("Flooding", [
        # Actual occurrence only ("flooded" / recurring "floods" / knee-deep
        # water). Deliberately excludes bare "flooding" immediately followed
        # by "risk" -- a drain that is blocked and merely AT RISK of
        # flooding has not flooded yet; that is a Drain Blockage, not a
        # Flooding, until the water is actually described as present.
        r"\bflooded\b", r"\bfloods\b", r"\bflooding\b(?!\s*risk)",
        r"waterlog", r"knee-deep", r"inundat",
    ]),
    ("Drain Blockage", [
        r"drain block", r"drain.*blocked", r"stormwater drain",
        r"sewage block", r"main drain",
    ]),
    ("Pothole", [
        r"pothole",
    ]),
    ("Road Damage", [
        r"road collapsed", r"road surface", r"road subsid", r"road buckl",
        r"road caved", r"road crack", r"\bcrater\b", r"manhole cover",
        r"footpath broken", r"footpath tiles broken",
        r"paving upturned", r"upturned paving", r"\bupturned\b",
        r"broken bench", r"pavement broken", r"road damaged", r"sinking",
    ]),
    ("Streetlight", [
        r"streetlight", r"street light", r"lights? out", r"unlit",
        r"lamp\s?post", r"substation tripped", r"flickering", r"sparking",
    ]),
    ("Waste", [
        r"garbage", r"\bwaste\b", r"\btrash\b", r"\blitter\b",
        r"dead animal", r"overflowing bin", r"bins? overflow",
    ]),
    ("Noise", [
        r"\bnoise\b", r"\bmusic\b", r"\bloud\b", r"drilling",
        r"amplifier", r"band playing", r"idling",
    ]),
]

# Heritage mentions that DON'T clearly describe damage to the heritage asset
# itself (e.g. "heritage zone garbage overflow") are genuinely ambiguous
# between Heritage Damage and whatever else matched — flag for review.
AMBIGUOUS_HERITAGE_MENTION = re.compile(r"heritage|historic|ancient")


def _find_matches(patterns, text):
    return [p for p in patterns if re.search(p, text)]


def _quote_evidence(description: str, patterns_matched, fallback_words=None) -> str:
    """Pull the literal snippet(s) of the description that matched, for the
    audit-ready `reason` field (agents.md: reason must quote real words)."""
    quotes = []
    for pat in patterns_matched:
        m = re.search(pat, description, flags=re.IGNORECASE)
        if m:
            quotes.append(m.group(0))
    if not quotes and fallback_words:
        quotes = fallback_words
    # De-duplicate while preserving order.
    seen = []
    for q in quotes:
        if q.lower() not in [s.lower() for s in seen]:
            seen.append(q)
    return ", ".join(f"'{q}'" for q in seen[:4])


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    try:
        description = row.get("description") or ""
        desc_lower = description.lower()

        if not description.strip():
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Standard",
                "reason": "description field was empty; cannot classify without complaint text.",
                "flag": "NEEDS_REVIEW",
            }

        # --- Category: fixed enum, deterministic priority order ------------
        category = "Other"
        matched_patterns = []
        for cat_name, patterns in CATEGORY_RULES:
            hits = _find_matches(patterns, desc_lower)
            if hits:
                category = cat_name
                matched_patterns = hits
                break

        flag = ""
        if category == "Other":
            flag = "NEEDS_REVIEW"
        elif category != "Heritage Damage" and AMBIGUOUS_HERITAGE_MENTION.search(desc_lower):
            # Heritage language present but a different category won the
            # match (e.g. "heritage zone garbage overflow") -- genuinely
            # ambiguous between Heritage Damage and the matched category.
            flag = "NEEDS_REVIEW"

        # --- Priority: severity keywords checked FIRST, unconditionally ----
        severity_hits = [kw for kw in SEVERITY_KEYWORDS
                          if re.search(r"\b" + kw + r"\b", desc_lower)]
        if severity_hits:
            priority = "Urgent"
        elif category == "Noise":
            priority = "Low"
        else:
            priority = "Standard"

        # --- Reason: quote the real matched words ---------------------------
        reason_parts = []
        if severity_hits:
            reason_parts.append(
                f"Urgent: severity keyword(s) {_quote_evidence(description, [r'\\b' + k + r'\\b' for k in severity_hits])} found in description"
            )
        if category != "Other":
            reason_parts.append(
                f"category={category} matched on {_quote_evidence(description, matched_patterns)}"
            )
        else:
            reason_parts.append(
                "no category keyword matched this description; defaulted to Other for manual review"
            )
        reason = "; ".join(reason_parts) + "."

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    except Exception as exc:  # noqa: BLE001 - agents.md: never crash a row
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": f"classification failed on this row ({exc}); routed to Other for manual review.",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row; always produces one output row per input row.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "description" not in reader.fieldnames:
            raise ValueError(
                f"Input CSV '{input_path}' is missing a 'description' column. "
                f"Found columns: {reader.fieldnames}"
            )
        input_fieldnames = reader.fieldnames
        input_rows = list(reader)

    new_cols = ["category", "priority", "reason", "flag"]
    output_fieldnames = list(input_fieldnames) + new_cols

    urgent_count = 0
    review_count = 0
    output_rows = []
    for row in input_rows:
        result = classify_complaint(row)
        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            review_count += 1
        merged = dict(row)
        merged.update({k: result[k] for k in new_cols})
        output_rows.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(
        f"Classified {len(output_rows)} rows -> {output_path} "
        f"({urgent_count} Urgent, {review_count} flagged NEEDS_REVIEW)"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
