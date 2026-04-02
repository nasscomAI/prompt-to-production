"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS_URGENT = [
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


def _lower(s: object) -> str:
    if s is None:
        return ""
    return str(s).lower()


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(n in text for n in needles)


def _category_candidates(description: str) -> tuple[str, list[str]]:
    """
    Returns (best_category, evidence_tokens).
    If ambiguous, best_category will be "Other" and evidence_tokens may contain multiple signals.
    """
    desc = _lower(description)

    # Scoring is intentionally simple/deterministic:
    # - primary keywords contribute 2 points
    # - secondary keywords contribute 1 point
    # - ties are treated as "genuinely ambiguous" -> Other + NEEDS_REVIEW
    rules: list[tuple[str, list[str], list[str]]] = [
        # Drain Blockage: prefer the existence of drain-related terms and "blocked" style evidence.
        ("Drain Blockage", ["main drain", "stormwater drain", "drainage", "drain"], ["blocked", "blockage"]),
        ("Pothole", ["potholes", "pothole"], []),
        ("Heritage Damage", ["heritage zone", "heritage"], []),
        ("Road Damage", ["road collapsed", "collapsed partially", "crater"], ["collapse"]),
        # Flooding: includes direct flood terms, plus softer rain-water language.
        ("Flooding", ["flooding", "flooded", "flood"], ["rainwater", "stormwater"]),
        ("Waste", ["garbage", "trash", "waste", "piles"], ["overflow", "not cleared"]),
        ("Noise", ["noise"], ["drilling", "idling", "engines", "engine"]),
        ("Streetlight", ["street light", "streetlight", "streetlights"], []),
        ("Heat Hazard", ["heat hazard", "heat", "hot"], []),
    ]

    scores: dict[str, int] = {c: 0 for c in ALLOWED_CATEGORIES}
    evidence: dict[str, list[str]] = {c: [] for c in ALLOWED_CATEGORIES}

    for category, primary, secondary in rules:
        primary_hits = [kw for kw in primary if kw in desc]
        secondary_hits = [kw for kw in secondary if kw in desc]

        if primary_hits:
            scores[category] += 2
            # Prefer the most specific matched phrases first.
            unique_primary = list(dict.fromkeys(primary_hits))
            unique_primary.sort(key=len, reverse=True)
            evidence[category].extend(unique_primary[:2])

        if secondary_hits:
            scores[category] += 1
            unique_secondary = list(dict.fromkeys(secondary_hits))
            unique_secondary.sort(key=len, reverse=True)
            evidence[category].extend(unique_secondary[:2])

    max_score = max(scores.values())
    if max_score == 0:
        # Nothing matched: genuinely ambiguous in a workshop sense.
        return "Other", []

    top = [c for c, sc in scores.items() if sc == max_score and c != "Other"]
    if len(top) != 1:
        # Multiple strong signals.
        ev: list[str] = []
        for c in top:
            ev.extend(evidence[c][:2])
        # De-duplicate while preserving order.
        seen = set()
        ev = [x for x in ev if not (x in seen or seen.add(x))]
        return "Other", ev[:4]

    chosen = top[0]
    return chosen, evidence[chosen][:3]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""
    desc_l = _lower(description)

    severity_lower = [k.lower() for k in SEVERITY_KEYWORDS_URGENT]
    urgent_triggers = [k for k in severity_lower if k in desc_l]
    urgent = len(urgent_triggers) > 0
    priority = "Urgent" if urgent else "Standard"

    category, evidence_tokens = _category_candidates(description)

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # Reason: one sentence, must cite specific words from description.
    if category != "Other":
        category_token = evidence_tokens[:1][0] if evidence_tokens else "(description keywords)"
        if urgent:
            # Include a severity keyword so "Urgent" is justified in the same sentence.
            reason_token = urgent_triggers[0]
            reason = (
                f"Description mentions severity keyword '{reason_token}' and category signal '{category_token}', "
                f"indicating {category} and priority Urgent."
            )
        else:
            reason = f"Description mentions '{category_token}', which indicates category {category}."
    else:
        if evidence_tokens and urgent:
            cited = ", ".join([f"'{t}'" for t in evidence_tokens])
            reason = (
                f"Description mentions severity keyword '{urgent_triggers[0]}' but has ambiguous category signals "
                f"({cited}), so it is marked for review."
            )
        elif evidence_tokens:
            cited = ", ".join([f"'{t}'" for t in evidence_tokens])
            reason = f"Description contains potentially conflicting signals ({cited}), so the category is ambiguous."
        elif urgent:
            reason = (
                f"Description mentions severity keyword '{urgent_triggers[0]}' but no clear category indicators from "
                f"the allowed list, so it is marked for review."
            )
        else:
            reason = "Description did not contain clear category indicators from the allowed list, so it needs review."

    # Final schema enforcement: allowed values only.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if flag and flag != "NEEDS_REVIEW":
        flag = "NEEDS_REVIEW"

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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results: list[dict] = []

    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Basic null-safety: description is required for keyword matching.
                if row.get("description") is None or str(row.get("description")).strip() == "":
                    results.append(
                        {
                            "complaint_id": row.get("complaint_id", ""),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Missing description text; cannot classify category.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
                    continue

                results.append(classify_complaint(row))
            except Exception as e:
                # Never crash the batch run; produce a conservative fallback row.
                description = row.get("description", "") if isinstance(row, dict) else ""
                results.append(
                    {
                        "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed due to an error: {type(e).__name__}.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
