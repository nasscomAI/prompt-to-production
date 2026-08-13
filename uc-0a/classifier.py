"""
UC-0A — Complaint Classifier
Rule-based triage agent built from agents.md + skills.md (RICE workflow).
"""
import argparse
import csv
import re

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

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category detection rules (priority-ordered). Each keyword is a regex.
# First group with the highest match count wins; ties on count are broken by
# the priority order of this list.
CATEGORY_RULES = [
    ("Pothole", [r"\bpotholes?\b"]),
    ("Flooding", [r"\bflooded\b", r"\bflooding\b", r"\bfloods?\b", r"\bstanding in water\b", r"\brainwater\b"]),
    ("Drain Blockage", [r"\bdrain\w*\b", r"\bblocked\b"]),
    ("Streetlight", [
        r"\bstreetlights?\b", r"\bstreet lights?\b", r"\blights? out\b", r"\bunlit\b",
        r"\bspark\w*\b", r"\bflicker\w*\b", r"\bdark\w*\b", r"\bsubstation\w*\b", r"\bpower\b",
    ]),
    ("Waste", [
        r"\bgarbage\b", r"\bwaste\b", r"\bbins?\b", r"\bdead animal\b", r"\boverflow\w*\b",
        r"\bnot cleared\b", r"\bpiles?\b", r"\bsmell\w*\b",
    ]),
    ("Noise", [
        r"\bmusic\b", r"\bwedding\w*\b", r"\bamplifier\w*\b", r"\bclub\b", r"\bdrill\w*\b",
        r"\bband\b", r"\bidl\w*\b", r"\bnois\w*\b",
    ]),
    ("Heat Hazard", [
        r"\bheat\w*\b", r"\bmelt\w*\b", r"\btemperature\w*\b", r"\bsun\b",
        r"\bburn\w*\b", r"\bbubbl\w*\b", r"\bhot\b",
    ]),
    ("Heritage Damage", [r"\bheritage\b", r"\bhistoric\w*\b", r"\bancient\b"]),
    ("Road Damage", [
        r"\broad surface\b", r"\broad collapsed\b", r"\broad subsid\w*\b", r"\broad buckled\b",
        r"\bcrack\w*\b", r"\bsink\w*\b", r"\bsubsid\w*\b", r"\bbuckle\w*\b", r"\bcollaps\w*\b",
        r"\bcrater\w*\b", r"\bfootpath\w*\b", r"\bmanhole\b", r"\bpav\w*\b",
        r"\bcobblestone\w*\b", r"\btiles? broken\b", r"\bupturn\w*\b",
    ]),
]

# Ties between these category pairs are treated as genuinely ambiguous.
AMBIGUOUS_PAIRS = {
    frozenset(["Flooding", "Drain Blockage"]),
    frozenset(["Heritage Damage", "Road Damage"]),
}

# Cross-rule conflicts that are ambiguous regardless of scores.
CONFLICT_RULES = [
    (("flooded", "flooding", "floods", "standing in water"), ("drain", "blocked")),
]

_COMPILED = [(name, [re.compile(p) for p in patterns]) for name, patterns in CATEGORY_RULES]


def _matches(text: str, patterns) -> list:
    return [p.pattern for p in patterns if p.search(text)]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = row.get("description", "")

    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    text = str(description).lower()

    scored = []
    for name, patterns in _COMPILED:
        matched = _matches(text, patterns)
        if matched:
            scored.append((len(matched), name, matched[0]))

    if not scored:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": f"Description '{description}' matches no known category keywords.",
            "flag": "NEEDS_REVIEW",
        }

    rule_order = {name: i for i, (name, _) in enumerate(_COMPILED)}
    scored.sort(key=lambda item: (-item[0], rule_order[item[1]]))

    best_score, category, best_kw = scored[0]

    # Ambiguity: a tied top-two between known-ambiguous category pairs, a
    # cross-rule conflict (e.g. flooding plus a blocked drain), or an
    # out-of-schema safety signal (gas leak / fire).
    ambiguous = False
    if len(scored) > 1 and scored[1][0] == best_score:
        ambiguous = frozenset([category, scored[1][1]]) in AMBIGUOUS_PAIRS
    for first_group, second_group in CONFLICT_RULES:
        if any(k in text for k in first_group) and any(k in text for k in second_group):
            ambiguous = True
            break
    if "gas leak" in text or "gas pipeline" in text or "fire" in text:
        ambiguous = True

    flag = "NEEDS_REVIEW" if ambiguous else ""

    if any(kw in text for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = f"Cites '{best_kw}' — '{description}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    rows = []
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"No header row found in {input_path}")
        input_columns = list(reader.fieldnames)
        for row in reader:
            if not row or not any((str(v).strip() for v in row.values())):
                continue
            try:
                result = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001 — never crash a batch run
                result = {
                    "complaint_id": str(row.get("complaint_id", "")).strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            merged = dict(row)
            merged.update(result)
            rows.append(merged)

    output_columns = input_columns + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    n = batch_classify(args.input, args.output)
    print(f"Done. {n} rows. Results written to {args.output}")
