"""
UC-0A — Complaint Classifier (Ollama backend)
Implements: classify_complaint skill + batch_classify skill
Enforces:   agents.md enforcement rules (category allowlist, severity keywords,
            mandatory reason, NEEDS_REVIEW flag, taxonomy-drift check)
Run:        python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv

Requirements:
    pip install ollama
    ollama pull llama3          # or any model you prefer
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
from collections import defaultdict
from typing import Any

import ollama

# ---------------------------------------------------------------------------
# Configuration — change MODEL to any model you have pulled in Ollama
# ---------------------------------------------------------------------------

OLLAMA_MODEL = "llama3"   # e.g. "mistral", "phi3", "gemma2", etc.

# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES: list[str] = [
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

ALLOWED_PRIORITIES: list[str] = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS: list[str] = [
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

OUTPUT_FIELDS: list[str] = ["category", "priority", "reason", "flag"]
CATEGORY_SET: set[str] = set(ALLOWED_CATEGORIES)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("uc-0a")

# ---------------------------------------------------------------------------
# Enforcement helpers
# ---------------------------------------------------------------------------


def has_severity_keyword(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in SEVERITY_KEYWORDS)


def enforce_severity(description: str, priority: str) -> str:
    if has_severity_keyword(description) and priority != "Urgent":
        log.warning(
            "Severity keyword detected but model returned priority='%s'. "
            "Overriding to Urgent (severity-blindness guard).",
            priority,
        )
        return "Urgent"
    return priority


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are a municipal complaint classifier.

ALLOWED CATEGORIES (use EXACT strings, no variations):
{json.dumps(ALLOWED_CATEGORIES)}

ALLOWED PRIORITIES: {json.dumps(ALLOWED_PRIORITIES)}

SEVERITY KEYWORDS — if ANY of these appear in the description, priority MUST be "Urgent":
{json.dumps(SEVERITY_KEYWORDS)}

RULES:
1. category — pick one from the allowed list exactly as written. If nothing fits, use "Other".
2. priority — "Urgent" if any severity keyword appears (case-insensitive); else "Standard" or "Low".
3. reason — exactly ONE sentence that quotes or paraphrases specific words from the description.
4. flag — "NEEDS_REVIEW" if category is genuinely ambiguous; otherwise empty string "".

Respond with ONLY a valid JSON object. No markdown, no explanation, no extra text.
Example:
{{"category": "Pothole", "priority": "Standard", "reason": "Complainant mentions 'deep pothole' on main road.", "flag": ""}}
"""


def call_ollama(description: str) -> dict:
    """Call Ollama and return parsed JSON dict."""
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this complaint:\n\n{description}"},
        ],
        options={"temperature": 0},
    )

    raw = response["message"]["content"].strip()

    # Strip accidental markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    # Extract first JSON object if model adds extra text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model output: {raw!r}")

    return json.loads(match.group())


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------


def classify_complaint(row: dict[str, Any]) -> dict[str, Any]:
    description: str = str(row.get("description", "")).strip()

    # error_handling: missing_description
    if not description:
        log.warning("Row has missing/blank description. Applying fallback values.")
        result = dict(row)
        result["category"] = "Other"
        result["priority"] = "Low"
        result["reason"] = "No description provided — cannot classify."
        result["flag"] = "NEEDS_REVIEW"
        return result

    parsed = call_ollama(description)

    # Enforce category allowlist
    category = str(parsed.get("category", "")).strip()
    if category not in CATEGORY_SET:
        log.warning(
            "Model returned category '%s' outside allowlist. Replacing with 'Other'.",
            category,
        )
        category = "Other"
        parsed["flag"] = "NEEDS_REVIEW"

    # Enforce priority
    priority = str(parsed.get("priority", "Standard")).strip()
    if priority not in ALLOWED_PRIORITIES:
        log.warning("Model returned invalid priority '%s'. Defaulting to 'Standard'.", priority)
        priority = "Standard"

    # Severity keyword hard override
    priority = enforce_severity(description, priority)

    # Enforce reason non-empty
    reason = str(parsed.get("reason", "")).strip()
    if not reason:
        log.warning("Model returned empty reason. Applying fallback.")
        reason = "Description too vague to cite specific evidence."
        parsed["flag"] = "NEEDS_REVIEW"

    # Enforce flag values
    flag = str(parsed.get("flag", "")).strip()
    if flag not in ("NEEDS_REVIEW", ""):
        log.warning("Model returned invalid flag '%s'. Resetting to blank.", flag)
        flag = ""

    result = dict(row)
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    return result


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------


def batch_classify(input_path: str, output_path: str) -> None:

    # error_handling: file_not_found
    if not os.path.exists(input_path):
        log.error(
            "Input file not found: '%s'. Cannot continue — no output file created.",
            input_path,
        )
        sys.exit(1)

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            log.error("Input CSV has no headers. Aborting.")
            sys.exit(1)
        rows: list[dict] = list(reader)
        original_fieldnames: list[str] = list(reader.fieldnames)

    # error_handling: wrong_row_count
    if len(rows) != 15:
        log.warning(
            "Expected 15 rows but found %d. Processing all rows present.",
            len(rows),
        )

    results: list[dict] = []

    for idx, row in enumerate(rows):
        log.info("Classifying row %d / %d ...", idx + 1, len(rows))
        try:
            classified = classify_complaint(row)
        except Exception as exc:
            # error_handling: per_row_failure
            log.error("classify_complaint failed on row %d: %s", idx + 1, exc)
            classified = dict(row)
            classified["category"] = "Other"
            classified["priority"] = "Low"
            classified["reason"] = "Classification failed — see error log."
            classified["flag"] = "NEEDS_REVIEW"

        results.append(classified)

    # error_handling: taxonomy_drift_prevention
    _check_taxonomy_drift(results)

    # Build output fieldnames: original columns + four output fields (no duplicates)
    out_fieldnames = [f for f in original_fieldnames if f not in OUTPUT_FIELDS]
    out_fieldnames += OUTPUT_FIELDS

    # error_handling: output_write_failure
    try:
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=out_fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        log.info("Output written to '%s' (%d rows).", output_path, len(results))
    except OSError as exc:
        log.error(
            "Failed to write output file '%s': %s — results NOT saved.",
            output_path,
            exc,
        )
        sys.exit(1)


def _check_taxonomy_drift(results: list[dict]) -> None:
    fingerprint_to_categories: dict[str, set] = defaultdict(set)
    fingerprint_to_indices: dict[str, list] = defaultdict(list)

    for idx, row in enumerate(results):
        desc = str(row.get("description", "")).lower()
        words = desc.split()[:5]
        fp = " ".join(words)
        fingerprint_to_categories[fp].add(row.get("category", ""))
        fingerprint_to_indices[fp].append(idx + 1)

    for fp, cats in fingerprint_to_categories.items():
        if len(cats) > 1:
            log.warning(
                "Taxonomy drift detected — rows %s share description prefix '%s' "
                "but received different categories: %s",
                fingerprint_to_indices[fp],
                fp,
                cats,
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="classifier.py",
        description="UC-0A Complaint Classifier — batch classify via Ollama (no API key needed).",
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="INPUT_CSV",
        help="Path to the input CSV (e.g. ../data/city-test-files/test_pune.csv)",
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="OUTPUT_CSV",
        help="Path for the output CSV (e.g. results_pune.csv)",
    )
    parser.add_argument(
        "--model",
        default=OLLAMA_MODEL,
        metavar="MODEL",
        help=f"Ollama model name (default: {OLLAMA_MODEL}). Must be already pulled.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    global OLLAMA_MODEL
    OLLAMA_MODEL = args.model

    log.info("UC-0A Complaint Classifier  |  Ollama model: %s", OLLAMA_MODEL)
    log.info("Input:  %s", args.input)
    log.info("Output: %s", args.output)
    batch_classify(args.input, args.output)
    log.info("Done.")


if __name__ == "__main__":
    main()