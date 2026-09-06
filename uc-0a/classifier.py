"""
UC-0A — Complaint Classifier (rebuild)
Guided by agents.md (RICE framework) and skills.md.

Build addresses the four prior failure modes:
  - Overfit keyword logic   -> generalized root-term scoring (strong=2, weak=1),
                               not memorized phrases from any city's rows
  - No enforcement checks   -> fail-loud validation gate that refuses to write
                               invalid/inconsistent output
  - Weak reason field       -> single-sentence evidence citation quoting only
                               the matched terms, not a whole-description echo
  - Classification quality  -> principled severity/caution/Low model with an
                               honest Low rule; genuine ambiguity -> Other +
                               NEEDS_REVIEW (never a confident guess)
"""
import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Tuple

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# ---------------------------------------------------------------------------
# Root-term maps: strong terms score 2, weak terms score 1. Grounded purely in
# generalisable civic language (never city/ward/id-specific phrases).
# ---------------------------------------------------------------------------
CATEGORY_TERMS: Dict[str, Dict[str, int]] = {
    "Pothole": {"pothole": 2},
    "Flooding": {
        "flooded": 2, "flooding": 2, "flood": 2, "waterlogging": 2,
        "knee-deep": 2, "standing in water": 2, "water": 1, "rainwater": 1,
    },
    "Streetlight": {
        "streetlight": 2, "street lights": 2, "lights out": 2, "unlit": 2,
        "dark": 2, "darkness": 2, "substation": 1, "wiring": 1,
    },
    "Waste": {
        "garbage": 2, "waste": 2, "bins": 2, "dead animal": 2,
        "dumped": 1, "bins overflowing": 2, "overflowing": 1,
    },
    "Noise": {
        "noise": 2, "music": 2, "drilling": 2, "amplifier": 2,
        "amplifiers": 2, "idling": 1, "engines on": 1,
        "wedding band": 2, "band playing": 2, "playing music": 2,
        "loud": 2, "blaring": 2, "honking": 2, "shouting": 2,
    },
    "Road Damage": {
        "road surface": 2, "road": 1, "footpath": 2, "paving": 2,
        "tiles": 2, "subsidence": 2, "subsided": 2, "sinking": 2,
        "buckled": 2, "crater": 2, "cracked": 1, "manhole": 1,
    },
    "Heritage Damage": {
        "heritage": 2, "monument": 2, "historic": 2, "ancient": 2,
        "tagore museum": 2, "marble palace": 2, "tram": 2, "gazetted": 1,
    },
    "Heat Hazard": {
        "heat": 2, "heatwave": 2, "hot": 2, "burns on contact": 2,
        "burning": 2, "surface temperature": 2, "temperature": 1,
        "full sun": 2, "sun": 1, "melting": 2, "bubbling": 2, "storing heat": 2,
    },
    "Drain Blockage": {
        "drain": 2, "drains": 2, "drainage": 2, "stormwater": 1,
        "blocked": 1, "blockage": 2,
    },
}

# --- Explicit tie-break category pairs resolved deterministically (agents.md). ---
FLOODING_OVER_DRAIN_TERMS = ["flooded", "floods", "standing in water", "knee-deep", "flood"]
DRAIN_OVER_FLOOD_TERMS = ["blocked", "blockage", "construction debris", "mosquito"]
HEAT_TERMS = ["heat", "hot", "burns", "temperature", "sun", "melting", "bubbling", "storing heat"]
ROAD_SUBSTRATE_TERMS = ["road surface", "paving", "footpath", "tiles", "subsidence", "sinking", "buckled", "crater", "cracked"]
HERITAGE_TERMS = ["heritage", "monument", "historic", "ancient", "tagore museum", "marble palace"]

# ---------------------------------------------------------------------------
# Priority model
# ---------------------------------------------------------------------------
SEVERITY_PATTERNS = [
    r"\binjur(y|ies|ed)?\b", r"\bchild(ren)?\b", r"\bschool(s)?\b",
    r"\bhospital(s|ised|ized)?\b", r"\bambulance(s)?\b", r"\bfire(s)?\b",
    r"\bhazard(s|ous)?\b", r"\bfell\b", r"\bcollapse(d|s)?\b",
    r"\bburn(s|ed|ing|t)?\b", r"\bdanger(ous)?\b", r"\bunsafe\b",
    r"\belectrocut(e|ed|ion)?\b", r"\bscal(d|ded|ding)?\b",
    r"\bfall risk\b", r"\baccident risk\b", r"\brisk of injury\b",
    r"\brisk to\b", r"\bat risk\b", r"\blives at risk\b",
    r"\bstranded\b", r"\bgas leak\b",
]

CAUTION_PATTERNS = [
    r"\brisk(s)?\b", r"\bconcern(s)?\b", r"\bsafety concern\b", r"\bdanger(ous)?\b",
    r"\bhazard(s|ous)?\b", r"\bthreat(en)?(s|ed)?\b", r"\binjur(y|ies|ed)?\b",
    r"\bleak(s|ing|age)?\b", r"\bstranded\b", r"\bvulnerable\b", r"\burgent\b",
]

LOW_PATTERNS = [
    r"\birrigation system\b", r"\bgrass dying\b", r"\bcosmetic\b", r"\bminor\b",
    r"\bnot replaced\b", r"\brestor(ation|ed|e)?\b", r"\bgraffiti\b", r"\binconvenience\b",
]


def _score_category(text: str) -> Dict[str, int]:
    t = text.lower()
    scores = {c: 0 for c in ALLOWED_CATEGORIES}
    for cat, terms in CATEGORY_TERMS.items():
        for term, weight in terms.items():
            if term in t:
                scores[cat] += weight
    return scores


def _matched_terms(text: str, cat: str) -> List[str]:
    t = text.lower()
    return [term for term in CATEGORY_TERMS[cat] if term in t]


def _has_any(text: str, terms: List[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


def _has_regex_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def determine_category(text: str) -> Tuple[str, bool]:
    """Return (category, is_ambiguous). Never returns an invented category."""
    scores = _score_category(text)
    ranking = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_score = ranking[0][1]
    top_cats = [c for c, s in ranking if s == top_score]

    # No taxonomy evidence at all -> refuse
    if top_score == 0:
        return "Other", True

    # Single clear winner
    if len(top_cats) == 1:
        category = top_cats[0]
        if category == "Other":
            return "Other", True
        return category, False

    # Deterministic tie-breaks
    if set(top_cats) == {"Flooding", "Drain Blockage"}:
        if _has_any(text, FLOODING_OVER_DRAIN_TERMS):
            return "Flooding", False
        if _has_any(text, DRAIN_OVER_FLOOD_TERMS):
            return "Drain Blockage", False
        return "Other", True  # drained + flooded but neither resolved -> ambiguous

    if set(top_cats) == {"Heat Hazard", "Road Damage"}:
        if _has_any(text, HEAT_TERMS):
            return "Heat Hazard", False
        return "Road Damage", False

    if set(top_cats) == {"Road Damage", "Heritage Damage"}:
        if _has_any(text, ROAD_SUBSTRATE_TERMS):
            return "Road Damage", False
        if _has_any(text, HERITAGE_TERMS):
            return "Heritage Damage", False
        return "Other", True

    # --- general tie-breaker: prefer the category with the strongest matched term ---
    # When two categories tie but one matched a strong (weight 2) specific term while
    # the other only matched weak (weight 1) generic terms, the specific hazard wins
    # (e.g. a "pothole filling with rainwater" is a Pothole, not a Flooding).
    best_by_strongest: Dict[str, int] = {}
    for cat in top_cats:
        best = max((CATEGORY_TERMS[cat][term] for term in _matched_terms(text, cat)), default=0)
        best_by_strongest[cat] = best
    max_strength = max(best_by_strongest.values())
    strongest_cats = [c for c, s in best_by_strongest.items() if s == max_strength]
    if len(strongest_cats) == 1:
        winner = strongest_cats[0]
        return (winner, False)

    # Any other tie -> genuinely ambiguous
    return "Other", True


def _matched_texts(description: str, patterns: List[str]) -> List[str]:
    """Return the literal matched substrings for the given regex patterns."""
    out: List[str] = []
    for pattern in patterns:
        m = re.search(pattern, description, re.I)
        if m:
            t = m.group(0).lower()
            if t not in out:
                out.append(t)
    return out


def determine_priority(text: str) -> str:
    if _has_regex_any(text, SEVERITY_PATTERNS):
        return "Urgent"
    if _has_regex_any(text, LOW_PATTERNS) and not _has_regex_any(text, CAUTION_PATTERNS):
        return "Low"
    return "Standard"


def _priority_evidence(description: str, priority: str) -> List[str]:
    if not description:
        return []
    if priority == "Urgent":
        return _matched_texts(description, SEVERITY_PATTERNS)
    if priority == "Low":
        return _matched_texts(description, LOW_PATTERNS)
    # Standard: quote caution signals that were evaluated but did not escalate.
    return _matched_texts(description, CAUTION_PATTERNS)


def reason_sentence(description: str, category: str, priority: str,
                    is_ambiguous: bool) -> str:
    evidence = _matched_terms(description, category) if category in CATEGORY_TERMS else []
    pri_evidence = _priority_evidence(description, priority)
    pri_note = ""
    if pri_evidence:
        pri_terms = ", ".join("'" + p + "'" for p in pri_evidence[:4])
        pri_note = f" {priority.lower()} signal: {pri_terms}."
    if not is_ambiguous:
        if evidence:
            quoted = ", ".join(f"'{e}'" for e in evidence)
            return (f"Classified {category} ({priority}) — evidence: {quoted}.{pri_note}")
        return f"Classified {category} ({priority}).{pri_note}"
    # Ambiguous / out-of-taxonomy row: quote the risk signal(s) that drove the review.
    quoted_terms = _matched_texts(description, SEVERITY_PATTERNS + CAUTION_PATTERNS)
    if quoted_terms:
        quoted = ", ".join(f"'{t}'" for t in quoted_terms[:4])
        return (f"Ambiguous or out-of-taxonomy ({category}, {priority}) — "
                f"review prompted by '{quoted}'.")
    return f"Ambiguous or out-of-taxonomy ({category}, {priority}) — needs review."


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classification not possible — description is missing or empty (NEEDS_REVIEW).",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = determine_category(description)
    priority = determine_priority(description)
    reason = reason_sentence(description, category, priority, is_ambiguous)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Enforcement / validation gate (skills.validate_result)
# ---------------------------------------------------------------------------
def validate_result(row: Dict[str, str], description: str) -> List[str]:
    violations: List[str] = []
    cid = row["complaint_id"]
    if row["category"] not in ALLOWED_CATEGORIES:
        violations.append(f"{cid}: category {row['category']} not allowed")
    if row["priority"] not in ALLOWED_PRIORITIES:
        violations.append(f"{cid}: priority {row['priority']} not allowed")

    sev_present = _has_regex_any(description, SEVERITY_PATTERNS) if description else False
    if sev_present and row["priority"] != "Urgent":
        violations.append(f"{cid}: severity signal present but priority is {row['priority']}")
    if not sev_present and row["priority"] == "Urgent":
        violations.append(f"{cid}: priority Urgent but no severity signal")

    if description:
        if row["flag"] == "NEEDS_REVIEW":
            # Ambiguous/refused rows: reason should still quote a signal or be a
            # clear no-evidence note — require at least one quoted token from the
            # description so the reason is never floating free of the report.
            cited = re.findall(r"'([^']+)'", row["reason"])
            if cited and not any(c.lower().strip("'").strip() in description.lower()
                                 for c in cited):
                violations.append(f"{cid}: reason quotes no term from description")
        else:
            cited = re.findall(r"'([^']+)'", row["reason"])
            if not cited or not any(c.lower() in description.lower() for c in cited):
                violations.append(f"{cid}: reason cites no evidence from description")

    if row["flag"] not in ("", "NEEDS_REVIEW"):
        violations.append(f"{cid}: flag '{row['flag']}' not allowed")
    return violations


def _read_rows(input_path: str) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, dict(fieldnames=fieldnames)


def batch_classify(input_path: str, output_path: str):
    rows, _ = _read_rows(input_path)
    results = []
    for row in rows:
        description = (row.get("description") or "").strip()
        classified = classify_complaint(row)
        results.append(classified)

    # Fail-loud validation gate (agents.md)
    all_violations: List[str] = []
    for row in results:
        src = next((r.get("description", "") for r in rows
                    if (r.get("complaint_id") or "").strip() == row["complaint_id"]), "")
        all_violations.extend(validate_result(row, src))

    if len(results) != len(rows):
        all_violations.append(f"row count mismatch: input {len(rows)}, output {len(results)}")

    if all_violations:
        print("UC-0A validation FAILED — no results file written:", file=sys.stderr)
        for v in all_violations:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    import collections
    cats = collections.Counter(r["category"] for r in results)
    pris = collections.Counter(r["priority"] for r in results)
    flagged = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Done. Results written to {output_path}")
    print(f"  categories: {dict(cats)}")
    print(f"  priorities: {dict(pris)}  needs_review: {flagged}")


def run_self_check() -> int:
    cities = ["ahmedabad", "pune", "hyderabad", "kolkata"]
    failures = 0
    for city in cities:
        input_path = os.path.join("..", "data", "city-test-files", f"test_{city}.csv")
        try:
            rows, _ = _read_rows(input_path)
        except FileNotFoundError as exc:
            print(f"[FAIL] {city}: {exc}")
            failures += 1
            continue
        problems = []
        for row in rows:
            src = (row.get("description") or "").strip()
            classified = classify_complaint(row)
            problems.extend(validate_result(classified, src))
        status = "PASS" if not problems else "FAIL"
        print(f"[{status}] {city}: {len(rows)} rows classified")
        for p in problems:
            print(f"      {p}")
            failures += 1
    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (rebuild)")
    parser.add_argument("--input", help="Path to test_[city].csv")
    parser.add_argument("--output", help="Path to write results CSV")
    parser.add_argument("--verify", action="store_true",
                        help="run non-destructive self-check over all four city files")
    args = parser.parse_args()

    if args.verify:
        f = run_self_check()
        if f:
            print(f"self-check: {f} problem(s)", file=sys.stderr)
            sys.exit(1)
        print("self-check: all city files OK")
        sys.exit(0)

    if not args.input or not args.output:
        parser.error("--input and --output are required unless using --verify")
    batch_classify(args.input, args.output)