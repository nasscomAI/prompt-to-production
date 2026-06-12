"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in skills.md,
enforcing all rules specified in agents.md.
"""
import argparse
import csv
import os
import re
import sys

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# ---------------------------------------------------------------------------
# Schema constants — agents.md enforcement anchors
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

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
}

HEDGING_PHRASES = [
    "possibly", "might be", "could indicate", "appears to be",
    "generally", "typically", "it seems", "may be", "perhaps",
    "could be", "it could", "it may",
]

DESCRIPTION_COLUMN = "description"

OUTPUT_COLUMNS = ["category", "priority", "reason", "flag"]

# ---------------------------------------------------------------------------
# Prompt template — enforces every rule from agents.md at the LLM boundary
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a complaint classification agent.

ALLOWED CATEGORIES (use exact strings only, no variations):
Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other

ALLOWED PRIORITIES (use exact strings only):
Urgent, Standard, Low

SEVERITY KEYWORDS — if ANY of these words appear in the description, priority MUST be Urgent:
injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

RULES:
1. Return exactly four fields: category, priority, reason, flag.
2. category must be one of the ten allowed strings above. Do not invent new names, abbreviations, or compound labels.
3. priority must be Urgent if a severity keyword appears in the description. This rule overrides all other judgment.
4. reason must be ONE sentence that quotes or directly references specific words from the input description. Do not use hedging phrases such as: possibly, might be, could indicate, appears to be, generally, typically, it seems.
5. flag must be NEEDS_REVIEW if the description maps with equal plausibility to more than one category. Otherwise flag must be empty.
6. If the description does not fit any named category, use Other — never invent sub-categories.
7. Each complaint is classified independently. Do not reference or infer from any prior row.

OUTPUT FORMAT — respond with exactly these four lines and nothing else:
category: <value>
priority: <value>
reason: <value>
flag: <value or blank>
"""


def _contains_severity_keyword(text: str) -> bool:
    """Return True if any severity keyword appears as a word in the text."""
    lower = text.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower):
            return True
    return False


def _contains_hedging(text: str) -> bool:
    """Return True if the reason contains a banned hedging phrase."""
    lower = text.lower()
    return any(phrase in lower for phrase in HEDGING_PHRASES)


def _parse_llm_response(raw: str) -> dict:
    """
    Parse the LLM's four-line response into a dict.
    Returns keys: category, priority, reason, flag.
    Raises ValueError if any required field is missing.
    """
    result = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key in OUTPUT_COLUMNS:
                result[key] = value

    missing = [col for col in OUTPUT_COLUMNS if col not in result]
    if missing:
        raise ValueError(f"LLM response missing fields: {missing}\nRaw: {raw!r}")
    return result


def _enforce_rules(description: str, result: dict) -> dict:
    """
    Post-call enforcement layer — corrects any agents.md violations
    that the LLM output may contain, and logs a warning for each fix.
    """
    # Rule: category must be in allowed set
    if result["category"] not in ALLOWED_CATEGORIES:
        print(
            f"  [ENFORCE] Invalid category '{result['category']}' → replaced with 'Other'",
            file=sys.stderr,
        )
        result["category"] = "Other"

    # Rule: priority must be in allowed set
    if result["priority"] not in ALLOWED_PRIORITIES:
        print(
            f"  [ENFORCE] Invalid priority '{result['priority']}' → replaced with 'Standard'",
            file=sys.stderr,
        )
        result["priority"] = "Standard"

    # Rule: severity keyword always forces Urgent
    if _contains_severity_keyword(description) and result["priority"] != "Urgent":
        print(
            f"  [ENFORCE] Severity keyword detected but priority was '{result['priority']}' → set to 'Urgent'",
            file=sys.stderr,
        )
        result["priority"] = "Urgent"

    # Rule: flag must be NEEDS_REVIEW or blank
    if result["flag"] not in ("NEEDS_REVIEW", ""):
        print(
            f"  [ENFORCE] Invalid flag '{result['flag']}' → cleared to blank",
            file=sys.stderr,
        )
        result["flag"] = ""

    # Rule: reason must not contain hedging language
    if _contains_hedging(result["reason"]):
        print(
            "  [ENFORCE] Hedging language detected in reason → NEEDS_REVIEW set",
            file=sys.stderr,
        )
        result["flag"] = "NEEDS_REVIEW"

    # Rule: reason must not be empty
    if not result["reason"].strip():
        result["reason"] = f'Description text: "{description[:80]}" — no classifiable content found.'
        result["flag"] = "NEEDS_REVIEW"

    return result


def _call_llm(description: str) -> dict:
    """
    Send one complaint description to the LLM and return parsed, enforced output.
    Falls back to a rule-based classifier if no API key / genai not available.
    """
    if genai is None or not os.environ.get("GOOGLE_API_KEY"):
        return _rule_based_classify(description)

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    user_message = f'Classify this complaint:\n\n"{description}"'
    response = model.generate_content(user_message)
    raw = response.text

    result = _parse_llm_response(raw)
    return _enforce_rules(description, result)


# ---------------------------------------------------------------------------
# Rule-based fallback classifier
# Used when no LLM API key is available; also demonstrates the enforcement
# logic in isolation for unit-testing.
# ---------------------------------------------------------------------------

_CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "tyre damage", "potholes"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlog", "knee-deep", "water level"]),
    ("Streetlight",     ["streetlight", "street light", "lamp", "light out", "lights out",
                         "flickering", "sparking", "dark at night"]),
    ("Waste",           ["garbage", "waste", "rubbish", "litter", "dumped", "overflowing bin",
                         "dead animal", "bulk waste"]),
    ("Noise",           ["noise", "music", "loud", "midnight", "sound", "playing music"]),
    ("Road Damage",     ["road surface", "cracked", "sinking", "broken road", "road damage",
                         "footpath", "tiles broken", "upturned"]),
    ("Heritage Damage", ["heritage", "historical", "monument", "old city"]),
    ("Heat Hazard",     ["heat", "hot", "temperature", "sun", "heatwave"]),
    ("Drain Blockage",  ["drain blocked", "drain blockage", "manhole", "sewer", "blocked drain",
                         "clogged"]),
]


def _rule_based_classify(description: str) -> dict:
    """
    Keyword-based fallback classifier.
    Matches exactly the ten allowed categories.
    Sets NEEDS_REVIEW when two or more categories score equally.
    """
    lower = description.lower()

    scores: dict[str, int] = {}
    for category, keywords in _CATEGORY_KEYWORDS:
        score = sum(1 for kw in keywords if kw in lower)
        if score > 0:
            scores[category] = score

    # Determine category
    if not scores:
        category = "Other"
        flag = ""
    else:
        max_score = max(scores.values())
        top_categories = [c for c, s in scores.items() if s == max_score]
        if len(top_categories) > 1:
            category = top_categories[0]   # pick first alphabetically for determinism
            flag = "NEEDS_REVIEW"
        else:
            category = top_categories[0]
            flag = ""

    # Determine priority — severity keywords always win
    if _contains_severity_keyword(description):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Build reason — cite specific words from the description
    desc_words = description[:120].rstrip()
    reason = f'Description states "{desc_words}" which indicates {category}.'

    return _enforce_rules(description, {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    })


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(description: str) -> dict:
    """
    Skill: classify_complaint
    Input:  plain-text complaint description (str)
    Output: dict with keys — category, priority, reason, flag

    Error handling per skills.md:
    - Empty / missing description → Other, Low, canned reason, NEEDS_REVIEW
    - Invalid category from LLM   → replaced with Other (enforced post-call)
    - Severity keyword missed      → corrected to Urgent (enforced post-call)
    - Ambiguous classification     → NEEDS_REVIEW set
    - Hedging in reason            → NEEDS_REVIEW set
    """
    # Guard: empty description
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description field was empty — no content to classify.",
            "flag": "NEEDS_REVIEW",
        }

    return _call_llm(description)


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Skill: batch_classify
    Reads input CSV, applies classify_complaint to each row independently,
    and writes results CSV with original columns + category, priority, reason, flag.

    Error handling per skills.md:
    - Input file not found         → halt with error message
    - Missing description column   → halt with schema error
    - Empty description in a row   → classify (returns NEEDS_REVIEW), continue
    - Output directory not writable → halt with write error
    - Row independence guaranteed  → classify_complaint has no shared state
    """

    # --- Read input ---
    if not os.path.exists(input_path):
        print(
            f"ERROR: Input file not found: {input_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if DESCRIPTION_COLUMN not in (reader.fieldnames or []):
                print(
                    f"ERROR: Input file is missing required column '{DESCRIPTION_COLUMN}'. "
                    f"Found columns: {reader.fieldnames}",
                    file=sys.stderr,
                )
                sys.exit(1)

            input_rows = list(reader)
            original_fieldnames = list(reader.fieldnames)
    except OSError as exc:
        print(f"ERROR: Cannot read input file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Classify each row independently ---
    output_rows = []
    for i, row in enumerate(input_rows, start=1):
        description = row.get(DESCRIPTION_COLUMN, "")
        print(f"  Row {i}: classifying complaint id={row.get('complaint_id', '?')!r} ...", file=sys.stderr)

        result = classify_complaint(description)

        # Merge: original columns first, then the four new output columns
        out_row = {col: row.get(col, "") for col in original_fieldnames}
        for col in OUTPUT_COLUMNS:
            out_row[col] = result[col]

        output_rows.append(out_row)

    # --- Write output ---
    output_fieldnames = original_fieldnames + OUTPUT_COLUMNS
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        print(
            f"ERROR: Output directory does not exist: {output_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
    except OSError as exc:
        print(f"ERROR: Cannot write output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Verify row count integrity
    if len(output_rows) != len(input_rows):
        print(
            f"ERROR: Row count mismatch — input had {len(input_rows)} rows, "
            f"output has {len(output_rows)} rows.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"Done. {len(output_rows)} rows classified and written to {output_path}",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Entry point — matches the run command in the UC README
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — classifies civic complaints from a CSV file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file (e.g. ../data/city-test-files/test_pune.csv)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV (e.g. results_pune.csv)",
    )
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Results written to: {args.output}")
