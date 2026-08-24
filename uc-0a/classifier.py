"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Enforcement rule 1 -- see agents.md. Matched case-insensitively as substrings,
# which is what makes "child" catch "children" and "hazard" catch "hazards".
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Enforcement rules 4-6 -- see agents.md. Evaluated top to bottom; the first rule
# whose cue appears in the description wins, so the same text always yields the
# same category. Ordering decisions that matter:
#   Pothole before Road Damage    -- a pothole is the more specific defect
#   Streetlight before Heritage   -- "heritage street, lights out" is a lighting
#                                    fault on a heritage street, not damage to a
#                                    heritage structure
#   Flooding before Drain Blockage -- standing water is the citizen-facing
#                                    impact; a blocked drain is the cause
# "manhole" is a cue for both Drain Blockage and Road Damage. That is not a
# mistake: a manhole defect on a carriageway is simultaneously a drainage asset
# fault and a road surface hazard, so it should surface as ambiguous rather than
# be silently resolved to either one.
CATEGORY_RULES = [
    ("Pothole",         ["pothole"]),
    ("Streetlight",     ["streetlight", "street light", "lights out"]),
    ("Flooding",        ["flood", "waterlogg", "standing in water"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "manhole", "sewage"]),
    ("Noise",           ["noise", "music", "loudspeaker"]),
    # "dead animal" is deliberately NOT a Waste cue. Carcass removal is a
    # separate statutory public-health service in Indian municipal corporations,
    # not solid waste collection, and this taxonomy has no category for it.
    # Filing it under Waste would route it to the wrong department, so it falls
    # through to Other and is flagged for a human.
    ("Waste",           ["garbage", "waste", "dumped", "refuse", "litter"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat", "heatwave"]),
    ("Road Damage",     ["road surface", "cracked", "sinking", "footpath", "tiles",
                         "manhole"]),
]


def _quote(words):
    """Render matched words as a quoted list so the reason cites source text.

    De-duplicates while preserving order: one cue can belong to more than one
    category, and citing it twice reads as two pieces of evidence when there is
    only one.
    """
    seen = []
    for word in words:
        if word not in seen:
            seen.append(word)
    return ", ".join("'{}'".format(w) for w in seen)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority
    """
    text = row.get("description", "").lower()

    # Collect every category whose cues appear, not just the first. More than one
    # match means the complaint is genuinely ambiguous and must be flagged rather
    # than resolved silently (enforcement rule 8).
    matched = []
    for name, cues in CATEGORY_RULES:
        hits = [cue for cue in cues if cue in text]
        if hits:
            matched.append((name, hits))

    if matched:
        category, cues_hit = matched[0]
    else:
        category, cues_hit = "Other", []

    # Enforcement: severity keywords force Urgent, checked before any other
    # priority logic. days_open is deliberately not consulted -- elapsed time is
    # a backlog metric, not a risk signal.
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    priority = "Urgent" if severity_hits else "Standard"

    # Enforcement rule 9: Other is itself a reviewable event.
    # Enforcement rule 8: more than one competing category is too.
    if not matched:
        flag = "NEEDS_REVIEW"
        reason = "No category cue found in the description, so classified Other."
    elif len(matched) > 1:
        flag = "NEEDS_REVIEW"
        competing = " and ".join(name for name, _ in matched)
        reason = "Description cues {} match competing categories {}.".format(
            _quote(cue for _, hits in matched for cue in hits), competing
        )
    else:
        flag = ""
        reason = "Description contains {}.".format(_quote(cues_hit))

    if severity_hits:
        reason += " Priority Urgent: description contains {}.".format(_quote(severity_hits))

    # Enforcement rule 4 is a claim about output, so it is checked against output
    # rather than trusted. A mistyped rule name would otherwise emit an invalid
    # category silently -- the exact failure this classifier exists to prevent.
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            "category {!r} is not one of the ten permitted values: {}".format(
                category, ", ".join(ALLOWED_CATEGORIES)
            )
        )

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [classify_complaint(row) for row in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


def selftest():
    """Assert the enforcement rules in agents.md actually hold. Run with --selftest."""

    def c(description, **extra):
        row = {"complaint_id": "T-1", "description": description}
        row.update(extra)
        return classify_complaint(row)

    # Rule 1: every severity keyword forces Urgent, whatever the category.
    for keyword in SEVERITY_KEYWORDS:
        assert c("pothole and %s here" % keyword)["priority"] == "Urgent", keyword
    # Substring matching is what makes the plural forms work.
    assert c("school children at risk")["priority"] == "Urgent"

    # Rule 2: days_open must never influence priority.
    assert c("overflowing garbage bins", days_open="999")["priority"] == "Standard"

    # Rule 3 and 4: values stay inside the permitted sets.
    for text in ["pothole", "flooded", "streetlight out", "garbage", "loud music", ""]:
        out = c(text)
        assert out["category"] in ALLOWED_CATEGORIES, out
        assert out["priority"] in ("Urgent", "Standard", "Low"), out
        assert out["flag"] in ("NEEDS_REVIEW", ""), out

    # Rule 6: no cue means Other, never an invented category.
    assert c("the ward office was unhelpful")["category"] == "Other"

    # Rule 7: the reason must quote words that are really in the description.
    reason = c("deep pothole near the school")["reason"]
    assert "'pothole'" in reason and "'school'" in reason, reason

    # Rule 8: competing categories are flagged, not silently resolved.
    ambiguous = c("bus stand flooded, drain blocked")
    assert ambiguous["flag"] == "NEEDS_REVIEW", ambiguous
    assert "Flooding" in ambiguous["reason"] and "Drain Blockage" in ambiguous["reason"]
    # A single cue shared by two categories is cited once, not twice.
    assert c("manhole cover missing")["reason"].count("'manhole'") == 1

    # Rule 9: falling outside the taxonomy is itself reviewable.
    assert c("")["flag"] == "NEEDS_REVIEW"
    # Carcass removal is a real municipal service this taxonomy has no slot for.
    # It must fall through to Other and be flagged, not be forced into Waste.
    carcass = c("Dead animal not removed for 36 hours. Health concern.")
    assert carcass["category"] == "Other", carcass
    assert carcass["flag"] == "NEEDS_REVIEW", carcass

    # Rule 4 is enforced against output, not merely asserted in agents.md.
    _saved = CATEGORY_RULES[0]
    try:
        CATEGORY_RULES[0] = ("Potholes", ["pothole"])  # a plausible typo
        try:
            c("large pothole")
            raise AssertionError("invalid category was emitted without error")
        except ValueError:
            pass
    finally:
        CATEGORY_RULES[0] = _saved

    # Rule 10: Low is documented as never emitted.
    assert c("wedding music past midnight")["priority"] != "Low"

    # skills.md contract: a row missing its id is still emitted, not dropped.
    assert classify_complaint({"description": "pothole"})["complaint_id"] == ""

    print("selftest: all enforcement rules hold")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  help="Path to test_[city].csv")
    parser.add_argument("--output", help="Path to write results CSV")
    parser.add_argument("--selftest", action="store_true",
                        help="Check the agents.md enforcement rules and exit")
    args = parser.parse_args()

    if args.selftest:
        selftest()
    else:
        if not args.input or not args.output:
            parser.error("--input and --output are required unless --selftest is given")
        batch_classify(args.input, args.output)
        print("Done. Results written to {}".format(args.output))
