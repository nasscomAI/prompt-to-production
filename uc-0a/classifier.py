"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per the contracts in
skills.md, using the RICE system prompt defined in agents.md.

Runtime requirements:
  pip install openai
Environment variables:
  OPENAI_API_KEY  — required
  OPENAI_MODEL    — optional, defaults to gpt-4o-mini
"""
import argparse
import csv
import json
import os

# ---------------------------------------------------------------------------
# Enforcement constants — sourced directly from agents.md
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

# agents.md enforcement rule 2 — severity keywords that always trigger Urgent
URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

# ---------------------------------------------------------------------------
# RICE system prompt — mirrors agents.md role / intent / context / enforcement
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a civic complaint classification agent. Your sole responsibility is to
read individual citizen complaint descriptions and assign a structured
classification to each one. You do not resolve complaints, communicate with
citizens, or infer information beyond what is explicitly stated in the text.

For every complaint you receive produce a JSON object with exactly five fields:
  complaint_id  — echoed unchanged from input
  category      — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
                  Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  priority      — exactly one of: Urgent, Standard, Low
  reason        — one sentence quoting specific words from the description
  flag          — "NEEDS_REVIEW" if category is genuinely ambiguous, else ""

Enforcement rules (non-negotiable):
1. Category must be exactly one of the ten allowed values — no spelling variants,
   plurals, or sub-categories allowed.
2. Priority must be Urgent if the description contains any of: injury, child,
   school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive),
   even if the overall tone seems routine.
3. The reason field must be non-empty and must cite at least one specific word
   or phrase copied verbatim from the complaint description.
4. If the correct category cannot be determined from the description alone, set
   category to Other and flag to NEEDS_REVIEW. Never invent a category name.

Respond with valid JSON only — no markdown fences, no explanation, no extra text.
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _force_priority(description: str, llm_priority: str) -> str:
    """Override LLM priority with Urgent if any severity keyword is present.
    Guards against: Severity blindness (agents.md enforcement rule 2)."""
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in URGENT_KEYWORDS):
        return "Urgent"
    return llm_priority


def _sanitize_category(category: str) -> tuple:
    """Return (canonical_category, flag).
    Guards against: Taxonomy drift, Hallucinated sub-categories (agents.md rule 1)."""
    if category in ALLOWED_CATEGORIES:
        return category, ""
    return "Other", "NEEDS_REVIEW"


def _call_llm(complaint_id: str, description: str) -> dict:
    """Send one complaint to the LLM using the RICE system prompt."""
    import openai  # local import — module usable without openai installed

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    user_message = json.dumps({"complaint_id": complaint_id, "description": description})
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# classify_complaint — skill contract from skills.md
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Skill contract (skills.md):
    - Input:  dict with complaint_id (str) and description (str).
    - Output: five-field dict matching the README classification schema.
    - Never raises an exception; all paths return a complete output dict.
    - Applies all agents.md enforcement rules on top of the LLM response.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description  = str(row.get("description",  "")).strip()

    # --- Error handling: missing / empty description (skills.md contract) ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided",
            "flag":         "NEEDS_REVIEW",
        }

    try:
        result = _call_llm(complaint_id, description)

        # Enforcement rule 1 — taxonomy guard
        raw_category      = result.get("category", "Other")
        category, flag    = _sanitize_category(raw_category)

        # Preserve NEEDS_REVIEW when LLM flagged ambiguity on a valid category
        if result.get("flag", "") == "NEEDS_REVIEW":
            flag = "NEEDS_REVIEW"

        # Enforcement rule 2 — priority keyword override (must run after LLM)
        raw_priority = result.get("priority", "Standard")
        if raw_priority not in ALLOWED_PRIORITIES:
            raw_priority = "Standard"
        priority = _force_priority(description, raw_priority)

        # Enforcement rule 3 — non-empty reason
        reason = str(result.get("reason", "")).strip()
        if not reason:
            reason = f'Description states: "{description[:80]}"'

        return {
            "complaint_id": complaint_id,
            "category":     category,
            "priority":     priority,
            "reason":       reason,
            "flag":         flag,
        }

    except Exception:
        # Row-level fault isolation — never crash (skills.md contract)
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Classification error",
            "flag":         "NEEDS_REVIEW",
        }


# ---------------------------------------------------------------------------
# batch_classify — skill contract from skills.md
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Skill contract (skills.md):
    - Raises FileNotFoundError immediately if input_path cannot be opened.
    - Never silently drops rows; every input row produces exactly one output row.
    - Output CSV columns (in order): complaint_id, category, priority, reason, flag.
    - Output file is always written as long as the input file was opened successfully.
    """
    # FileNotFoundError propagates immediately (skills.md contract)
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = [classify_complaint(row) for row in rows]  # never raises

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
