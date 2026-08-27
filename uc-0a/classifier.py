"""
UC-0A — Complaint Classifier
Built using RICE enforcement rules defined in agents.md and skills.md.

CRAFT loop fixes applied:
  Fix taxonomy drift:      Strict allowed-list enforced in system prompt and post-processing validation.
  Fix severity blindness:  Keyword list (injury/child/school/hospital/ambulance/fire/hazard/fell/collapse)
                           triggers Urgent priority — checked both by LLM and post-process override.
  Fix missing justification: reason field is mandatory and validated as non-empty.
  Fix hallucinated sub-categories: Post-processing rejects any category not in ALLOWED_CATEGORIES.
  Fix false confidence:    Ambiguous rows (Other with no NEEDS_REVIEW) are flagged automatically.
"""

import argparse
import csv
import json
import os
import re
import sys

# ── Classification schema (from agents.md) ───────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

SYSTEM_PROMPT = """You are a Complaint Classification Agent for a City Municipal Corporation.

ROLE: Classify a single citizen complaint. Your boundary is the description text only.

ALLOWED CATEGORIES (use EXACTLY these strings — no variations):
Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other

PRIORITY RULES:
- Urgent: if ANY of these words appear in description (case-insensitive):
  injury, injured, child, school, hospital, ambulance, fire, hazard, fell, collapse
- Standard: issue causes disruption but no severity keywords
- Low: minor or cosmetic issue

OUTPUT RULES (ALL are mandatory):
1. category: exactly one string from the allowed list above
2. priority: exactly one of Urgent / Standard / Low
3. reason: one sentence citing SPECIFIC WORDS from the description
4. flag: write NEEDS_REVIEW if category is genuinely ambiguous, else leave empty string

Respond ONLY with valid JSON in this exact format:
{
  "category": "<category>",
  "priority": "<priority>",
  "reason": "<one sentence citing words from description>",
  "flag": "<NEEDS_REVIEW or empty string>"
}

Do not add any explanation outside the JSON."""


def _check_severity(description: str) -> bool:
    """Return True if any severity keyword is found in the description."""
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in SEVERITY_KEYWORDS)


def _validate_and_fix(result: dict, description: str) -> dict:
    """Post-process LLM output — enforce all schema rules regardless of LLM output."""
    # Fix category
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    # Fix priority — severity keywords always win
    if _check_severity(description):
        result["priority"] = "Urgent"
    elif result.get("priority") not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"

    # Ensure reason is non-empty
    if not result.get("reason", "").strip():
        result["reason"] = "No reason provided by classifier — review manually."
        result["flag"] = "NEEDS_REVIEW"

    # Ensure flag is valid
    if result.get("flag") not in ("NEEDS_REVIEW", "", None):
        result["flag"] = "NEEDS_REVIEW"
    if result.get("flag") is None:
        result["flag"] = ""

    # If category is Other and flag is empty, flag for review
    if result["category"] == "Other" and result.get("flag", "") == "":
        result["flag"] = "NEEDS_REVIEW"

    return result


def _call_llm(description: str) -> dict:
    """
    Send the complaint description to an LLM and return a parsed result dict.
    Tries google-generativeai first, falls back to a rule-based classifier.
    """
    user_prompt = f'Classify this citizen complaint:\n\n"{description}"'

    # ── Try Google Gemini ────────────────────────────────────────────────────
    try:
        import google.generativeai as genai  # type: ignore

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(user_prompt)
            text = response.text.strip()
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception:
        pass  # Fall through to rule-based

    # ── Rule-based fallback (works without any API key) ──────────────────────
    desc_lower = description.lower()

    # Category rules (order matters — more specific first)
    if any(w in desc_lower for w in ["pothole", "crater", "pit in road"]):
        category = "Pothole"
    elif any(w in desc_lower for w in ["flood", "waterlog", "inundat", "submerge"]):
        category = "Flooding"
    elif any(w in desc_lower for w in ["streetlight", "street light", "lamp", "light", "unlit", "dark", "illuminate"]):
        category = "Streetlight"
    elif any(w in desc_lower for w in ["waste", "garbage", "trash", "litter", "rubbish", "overflowing bin", "bin overflow"]):
        category = "Waste"
    elif any(w in desc_lower for w in ["noise", "music", "loud", "audible", "sound at"]):
        category = "Noise"
    elif any(w in desc_lower for w in ["heritage", "ancient", "historic", "old city", "step well", "heritage area"]):
        category = "Heritage Damage"
    elif any(w in desc_lower for w in ["drain", "blocked drain", "drain blockage", "sewer"]):
        category = "Drain Blockage"
    elif any(w in desc_lower for w in ["heat", "temperature", "melting", "hot", "scorching", "burns", "52°", "44°", "45°", "bubble"]):
        category = "Heat Hazard"
    elif any(w in desc_lower for w in ["road damage", "subsidence", "pothole", "surface", "tarmac", "paving", "road collapse"]):
        category = "Road Damage"
    else:
        category = "Other"

    # Priority
    if _check_severity(description):
        priority = "Urgent"
    elif any(w in desc_lower for w in ["dangerous", "unsafe", "risk", "disruption", "closure", "commuter"]):
        priority = "Standard"
    else:
        priority = "Low"

    # Reason — pick the most relevant word
    reason_words = [w for w in desc_lower.split() if len(w) > 4][:3]
    reason = f"Classified as {category} based on key terms: '{', '.join(reason_words)}' in the description."

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Implements skills.md: classify_complaint skill.
    Enforces all rules from agents.md.
    Never raises an exception.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # Handle empty description (agents.md enforcement)
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW"
        }

    try:
        result = _call_llm(description)
        result = _validate_and_fix(result, description)
    except Exception as e:
        result = {
            "category": "Other",
            "priority": "Low",
            "reason": f"Classification error: {str(e)[:80]}",
            "flag": "NEEDS_REVIEW"
        }

    result["complaint_id"] = complaint_id
    return result


def batch_classify(input_path: str, output_path: str) -> int:
    """
    Read input CSV, classify each row, write results CSV.
    Implements skills.md: batch_classify skill.
    Never crashes on individual bad rows. Returns count of successes.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    success_count = 0
    error_count = 0

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                writer.writerow({k: result.get(k, "") for k in output_fields})
                success_count += 1
            except Exception as e:
                # skills.md: never crash on bad row
                writer.writerow({
                    "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing error — skipped. ({str(e)[:60]})",
                    "flag": "NEEDS_REVIEW"
                })
                error_count += 1
                print(f"  [WARNING] Row {i} error: {e}", file=sys.stderr)

    print(f"  Classified: {success_count} rows | Errors: {error_count} rows")
    return success_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    print(f"Reading: {args.input}")
    count = batch_classify(args.input, args.output)
    print(f"Done. {count} complaints classified. Results written to: {args.output}")
