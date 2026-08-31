"""
UC-0A — Complaint Classifier
Rule-based, local, deterministic classifier.
Built from the RICE rules in agents.md and the skills in skills.md.

Classification favours SPECIFIC category evidence over generic words so that,
for example, a mere mention of "water"/"rain" does not force Flooding and a bare
"road"/"drain" does not force Road Damage / Drain Blockage.
"""
import argparse
import csv

# Exact allowed categories and priorities (see agents.md).
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

# Severity keywords that MUST force priority to Urgent.
SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

# Category rules. Each entry: (category, (specific_phrases, general_words)).
# Order matters: SPECIFIC phrases are checked first so that strong evidence wins
# over a coincidental generic word. Within a category, the specific phrases list
# must be checked before the general list.
CATEGORY_RULES = [
    # Pothole — very high specificity on "pothole" and "crater".
    ("Pothole", (["pothole", "crater"], [])),

    # Flooding — requires actual water accumulation, submergence, or flooding.
    # A bare "water"/"rain" is not enough. Checked before Drain Blockage so that
    # a complaint primarily about flooding (e.g. a flooded bus stand) is NOT
    # misclassified as Drain Blockage just because a drain is also mentioned.
    ("Flooding", (["flood", "submerge", "standing in water", "knee-deep",
                   "under water", "waterlogged"], [])),

    # Drain Blockage — requires EVIDENCE of a blocked/clogged drain. A bare
    # "drain" mention is not enough. When water has actually accumulated, the
    # Flooding rule above takes precedence.
    ("Drain Blockage", (["drain block", "drainage blocked", "drain blocked",
                         "blocked with", "completely blocked", "clogged"], [])),

    # Streetlight — specific lighting/power-outage evidence.
    ("Streetlight", (["streetlight", "street light", "lights out", "unlit",
                      "lamp post", "sparking", "flickering", "substation"], [])),

    # Heat Hazard — specific heat/surface-temperature evidence.
    ("Heat Hazard", (["heat", "temperature", "melt", "bubbling", "burning hot",
                      "52\u00b0c", "44\u00b0c", "45\u00b0c"], [])),

    # Heritage Damage — specific cultural/heritage asset evidence.
    ("Heritage Damage", (["heritage", "historic", "monument", "step well",
                          "tram road", "old city", "museum", "defaced"], [])),

    # Waste — specific waste evidence.
    ("Waste", (["garbage", "waste", "bins", "dead animal", "rubbish",
                "overflowing", "not cleared"], [])),

    # Noise — specific noise evidence.
    ("Noise", (["music", "noise", "amplifier", "audible", "drilling",
                "idling", "band"], [])),

    # Road Damage — requires damage-specific evidence, not a bare "road".
    ("Road Damage", (["footpath", "manhole", "tiles broken", "cracked",
                      "sinking", "collapsed", "buckled", "paving", "subsided",
                      "surface damage"], [])),

    # Fallback generic words. Only reached if a category matched nothing above.
    ("Drain Blockage", ([], ["drain", "drainage"])),
    ("Flooding", ([], ["water", "rain"])),
    ("Streetlight", ([], ["power", "dark", "lamp"])),
    ("Road Damage", ([], ["road"])),
]

# Keywords that hint the category is genuinely ambiguous even after matching.
AMBIGUOUS_HINTS = ["heritage", "old city", "historic", "legacy"]


def _find_category(lower: str):
    """
    Return the matched category, or "Other" if no rule matches.
    Specific phrases are checked before general words.
    """
    for cat, (specific, general) in CATEGORY_RULES:
        if any(p in lower for p in specific):
            return cat
    for cat, (specific, general) in CATEGORY_RULES:
        if any(g in lower for g in general):
            return cat
    return "Other"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    category = "Other"
    flag = ""

    if description:
        lower = description.lower()

        category = _find_category(lower)

        # Mark genuinely ambiguous cases for review (e.g. heritage lighting).
        if any(hint in lower for hint in AMBIGUOUS_HINTS) and category != "Other":
            flag = "NEEDS_REVIEW"

        # Priority: Urgent if any severity keyword is present (case-insensitive).
        if any(kw in lower for kw in SEVERITY_KEYWORDS):
            priority = "Urgent"
        else:
            priority = "Standard"

        reason = _build_reason(description, lower, category, priority)
    else:
        category = "Other"
        priority = "Standard"
        reason = "No description provided."
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _matching_phrases(lower: str):
    """Collect all category phrases (specific + general) present in the text."""
    matched = []
    for cat, (specific, general) in CATEGORY_RULES:
        for p in specific:
            if p in lower and p not in matched:
                matched.append(p)
        for g in general:
            if g in lower and g not in matched:
                matched.append(g)
    return matched


def _build_reason(description: str, lower: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason that cites meaningful phrases from the
    description and explains why the category and priority were chosen.
    """
    cleaned = " ".join(description.split())
    if not cleaned:
        return "No description provided."

    # Find the phrases that actually match the assigned category.
    category_phrases = []
    for cat, (specific, general) in CATEGORY_RULES:
        if cat != category:
            continue
        for p in specific:
            if p in lower:
                category_phrases.append(cleaned[lower.index(p):lower.index(p) + max(len(p), 4)])
        for g in general:
            if g in lower:
                category_phrases.append(cleaned[lower.index(g):lower.index(g) + max(len(g), 4)])

    evidence = ", ".join('"%s"' % p.strip() for p in category_phrases[:3]) if category_phrases else 'the whole description'

    priority_explanation = {
        "Urgent": "Priority is Urgent because the description contains a severity keyword (%s).",
        "Standard": "Priority is Standard because no severity keyword is present.",
        "Low": "Priority is Low.",
    }[priority]

    # Pull out the exact severity keyword for Urgent reasons.
    if priority == "Urgent":
        present = [kw for kw in SEVERITY_KEYWORDS if kw in lower]
        priority_explanation = ("Priority is Urgent because the description "
                                "contains the severity keyword(s): %s."
                                % ", ".join('"%s"' % k for k in present))

    return 'Category %s because the description references %s. %s' % (
        category, evidence, priority_explanation)


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Produces one output row per complaint with columns:
    complaint_id, category, priority, reason, flag
    """
    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            # Malformed row: emit a safe stub so the batch does not crash.
            results.append(
                {
                    "complaint_id": row.get("complaint_id", "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Unable to classify row.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
