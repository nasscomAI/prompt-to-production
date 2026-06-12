"""
UC-0A — Complaint Classifier
Uses Groq API. Set GROQ_API_KEY in uc-0a/.env before running.
"""
import argparse
import csv
import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

_SYSTEM_PROMPT = """You are a citizen complaint classifier. Classify each complaint using ONLY the words in the complaint description — no external knowledge.

ALLOWED CATEGORIES (exact strings, no variations):
Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other

PRIORITY RULES:
- "Urgent"   — description contains ANY of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive)
- "Standard" — moderate impact, no severity keyword
- "Low"      — minor inconvenience, no severity keyword

REASON RULE:
Write exactly one sentence that quotes or paraphrases specific words from the description.
Never write a generic reason like "this is a complaint about potholes."

FLAG RULE:
- "NEEDS_REVIEW" — the correct category is genuinely ambiguous between two or more allowed values
- ""             — category is clear

Respond with valid JSON only — no markdown, no commentary:
{
  "category": "<one of the 10 allowed strings>",
  "priority": "Urgent" | "Standard" | "Low",
  "reason": "<one sentence citing words from the description>",
  "flag": "NEEDS_REVIEW" | ""
}"""


def _has_severity_keyword(description: str) -> bool:
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in SEVERITY_KEYWORDS)


def _normalize_category(raw: str) -> str:
    """Return the allowed category string, falling back to Other."""
    if raw in ALLOWED_CATEGORIES:
        return raw
    for allowed in ALLOWED_CATEGORIES:
        if allowed.lower() == raw.strip().lower():
            return allowed
    return "Other"


def classify_complaint(row: dict, client: Groq) -> dict:
    """skill: classify_complaint — one complaint row in, four fields out."""
    description = row.get("description", "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Complaint description: {description}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Model returned non-JSON output — justification gap.",
            "flag": "NEEDS_REVIEW",
        }
    except Exception as e:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": f"API error during classification: {e}",
            "flag": "NEEDS_REVIEW",
        }

    # Enforcement: taxonomy — never emit an invalid category string
    category = _normalize_category(result.get("category", ""))

    # Enforcement: severity keyword overrides model priority regardless of context
    priority = result.get("priority", "Standard")
    if _has_severity_keyword(description):
        priority = "Urgent"
    elif priority not in ("Urgent", "Standard", "Low"):
        priority = "Standard"

    reason = result.get("reason", "").strip()
    flag = result.get("flag", "")

    if not reason:
        reason = "Classification reason absent — justification gap detected."
        flag = "NEEDS_REVIEW"

    if flag not in ("NEEDS_REVIEW", ""):
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """skill: batch_classify — reads input CSV, classifies every row, writes output CSV."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        sys.exit("Error: GROQ_API_KEY environment variable is not set.")

    if not os.path.isfile(input_path):
        sys.exit(f"Error: Input file not found: {input_path}")

    # Verify the output path is writable before doing any work
    try:
        with open(output_path, "w"):
            pass
    except OSError as e:
        sys.exit(f"Error: Output path is not writable: {output_path} — {e}")

    client = Groq(api_key=api_key)

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])
    except OSError as e:
        sys.exit(f"Error: Cannot read input file: {input_path} — {e}")

    if "description" not in fieldnames:
        sys.exit(f"Error: Input file has no 'description' column: {input_path}")

    if all(not row.get("description", "").strip() for row in rows):
        sys.exit(f"Error: All 'description' values are empty in: {input_path}")

    # Strip columns that must be inferred, not read
    passthrough = [f for f in fieldnames if f not in ("category", "priority_flag")]
    output_fieldnames = passthrough + ["category", "priority", "reason", "flag"]

    output_rows = []
    for i, row in enumerate(rows, start=1):
        cid = row.get("complaint_id", f"row-{i}")
        print(f"  [{i}/{len(rows)}] {cid}")
        try:
            classification = classify_complaint(row, client)
        except Exception as e:
            classification = {
                "category": "Other",
                "priority": "Low",
                "reason": f"Unexpected error during classification: {e}",
                "flag": "NEEDS_REVIEW",
            }
        out_row = {k: v for k, v in row.items() if k in passthrough}
        out_row.update(classification)
        output_rows.append(out_row)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"\nDone. Results written to {args.output}")
