"""
UC-0A — Complaint Classifier

Classifies citizen complaints into schema-exact fields defined in README.md,
agents.md, and skills.md:

    category  - exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
                Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    priority  - Urgent if a severity keyword appears in the description, else Standard
    reason    - one sentence citing the specific words that drove the classification
    flag      - NEEDS_REVIEW when the category is genuinely ambiguous, else blank

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv

# Exact allowed category strings — no variations, no sub-categories.
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Keywords that must trigger priority=Urgent (README, agents.md enforcement).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard",
    "fell", "collapse",
]

# Keyword rules per category. A rule fires when ANY of its keywords appears in
# the (lowercased) description. Rules are intentionally narrow; a complaint that
# matches several rules is genuinely ambiguous and is flagged, not forced.
CATEGORY_RULES = [
    ("Pothole",        ["pothole", "crater", "crumbled road", "bump in the road"]),
    ("Flooding",       ["flood", "flooded", "waterlogging", "water logging",
                        "stagnant water", "water logged", "rainwater",
                        "water on road", "water accumulation"]),
    ("Streetlight",    ["streetlight", "street light", "street lamp", "lamp post",
                        "light not working", "not lit", "unlit", "dark",
                        "darkness", "power cut", "no power", "lights out"]),
    ("Waste",          ["waste", "garbage", "litter", "trash", "debris", "dumping",
                        "refuse", "dead animal", "stray animal", "carcass",
                        "overflow", "overflowing", "not cleared"]),
    ("Noise",          ["noise", "loud", "honking", "music", "speakers",
                        "construction noise", "dj", "drilling", "drill",
                        "idling", "idle", "loudspeaker", "amplifier",
                        "band playing", "wedding band", "live band"]),
    ("Road Damage",    ["road damage", "broken road", "damaged road", "crack",
                        "uneven road", "rutted", "pavement", "footpath",
                        "road surface", "sinkhole", "subsided", "subsidence",
                        "cobblestone", "cobblestones", "paving"]),
    ("Heritage Damage",["heritage", "monument", "fort", "temple", "historical",
                        "historic"]),
    ("Heat Hazard",    ["heat", "heatwave", "heat wave", "overheating",
                        "heat hazard", "scorching", "temperature", "melting",
                        "celsius", "full sun", "direct sun", "scorching sun",
                        "sun exposure"]),
    ("Drain Blockage", ["drain", "drainage", "sewer", "clogged", "manhole",
                        "blocked drain", "drain block", "blockage"]),
]

# Heritage Damage fires only when BOTH a heritage token and a damage signal are
# present. "Heritage zone / heritage area" is a location, not a damage complaint.
HERITAGE_TOKENS = ["heritage", "monument", "fort", "temple", "historical", "historic"]
DAMAGE_TOKENS = ["damage", "damaged", "vandal", "deface", "graffiti", "knocked",
                 "broken", "destroyed", "collapsed", "cracked", "demolish",
                 "deteriorat", "crack"]

# When a complaint's object dominates a secondary context signal, don't treat
# that as ambiguity: a pothole filling with rainwater is still a Pothole.
DOMINANT_IF_MATCHED = {  # weaker category -> stronger category
    "Flooding": "Pothole",
}


def _apply_dominance(active):
    """Drop a weaker category when a dominant one is also matched."""
    if len(active) > 1:
        cats = {c for c, _ in active}
        active = [
            (category, matched)
            for category, matched in active
            if category not in DOMINANT_IF_MATCHED
            or DOMINANT_IF_MATCHED[category] not in cats
        ]
    return active

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _matched_keywords(text: str, keywords) -> list:
    """Return the keywords present (case-insensitively) in text, in keyword order."""
    lowered = text.lower()
    return [kw for kw in keywords if kw in lowered]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    The classification is derived from the description alone — no external
    knowledge about the location or reporter is used.

    category: exactly one of CATEGORIES. "Other" when no rule fires or the
              description is genuinely ambiguous between several categories.
    priority: "Urgent" if any SEVERITY_KEYWORDS appears in the description,
              otherwise "Standard".
    reason:   one sentence citing the specific words that drove the decision.
    flag:     "NEEDS_REVIEW" when the description is missing/empty or the
              category is ambiguous; otherwise blank.
    """
    out = {
        "complaint_id": row.get("complaint_id", ""),
        "category": "",
        "priority": "",
        "reason": "",
        "flag": "",
    }

    description = (row.get("description") or "").strip()
    if not description:
        # No fabrication on unparseable rows (skills.md -> classify_complaint).
        out["reason"] = "INVALID ROW"
        out["flag"] = "NEEDS_REVIEW"
        return out

    hits = [
        (category, _matched_keywords(description, keywords))
        for category, keywords in CATEGORY_RULES
    ]
    # Suppress Heritage Damage unless the text also signals damage to the object,
    # so "Heritage zone garbage overflow" is Waste, not Waste + Heritage Damage.
    if _matched_keywords(description, HERITAGE_TOKENS) and not _matched_keywords(description, DAMAGE_TOKENS):
        hits = [(cat, matched) for cat, matched in hits if cat != "Heritage Damage"]
    active = _apply_dominance([(category, matched) for category, matched in hits if matched])

    if len(active) == 1:
        category, matched = active[0]
        out["category"] = category
        out["reason"] = f"Category {category} — description mentions: {', '.join(matched)}."
        out["flag"] = ""
    elif not active:
        out["category"] = "Other"
        out["reason"] = "No category keywords matched the description."
        out["flag"] = "NEEDS_REVIEW"
    else:
        names = ", ".join(category for category, _ in active)
        words = ", ".join(word for _, matched in active for word in matched)
        out["category"] = "Other"
        out["reason"] = f"Category ambiguous ({names}) — description mentions: {words}."
        out["flag"] = "NEEDS_REVIEW"

    severity = _matched_keywords(description, SEVERITY_KEYWORDS)
    if severity:
        out["priority"] = "Urgent"
        out["reason"] += f" Priority Urgent — description contains: {', '.join(severity)}."
    else:
        out["priority"] = "Standard"

    return out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Guarantees (skills.md -> batch_classify):
      - one output row per input row, in input order
      - a bad row never crashes the batch; it is flagged, not dropped
      - an output file is always produced, even when every row fails
    """
    with open(input_path, "r", newline="", encoding="utf-8") as in_fh:
        rows = list(csv.DictReader(in_fh))

    classified = []
    for row in rows:
        try:
            classified.append(classify_complaint(row))
        except Exception as exc:  # noqa: BLE001 — one bad row must not kill the batch
            classified.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "",
                "priority": "",
                "reason": f"INVALID ROW: {exc}",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as out_fh:
        writer = csv.DictWriter(out_fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(classified)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
