"""
UC-0A — Complaint Classifier
Classifies citizen complaints using the RICE enforcement rules defined in agents.md.
"""
import argparse
import csv
import os
import sys
import time

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)


ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

SYSTEM_PROMPT = """You are a Citizen Complaint Classification Agent for the City Municipal Corporation.

For each complaint, you must output EXACTLY a JSON object with these fields:
- "category": one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
- "priority": one of [Urgent, Standard, Low]
- "reason": one sentence citing specific words from the description
- "flag": "NEEDS_REVIEW" or ""

ENFORCEMENT RULES:
1. Category must be EXACTLY one of the 10 allowed values — no variations, no invented categories.
2. Priority must be Urgent if description contains ANY of these keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
3. Reason must cite specific words from the complaint description justifying the classification.
4. If the complaint is genuinely ambiguous (could equally be two categories), pick the best guess but set flag to "NEEDS_REVIEW".
5. Never invent sub-categories. If nothing fits, use "Other".
6. If description is empty, return: category="Other", priority="Low", reason="No description provided", flag="NEEDS_REVIEW".

Output ONLY valid JSON. No explanation, no markdown."""


def get_client_and_model():
    """Get the appropriate OpenAI client and model based on available API keys.
    Priority: OLLAMA_MODEL > GEMINI_API_KEY > OPENAI_API_KEY
    """
    # Ollama (local, free, no API key needed)
    ollama_model = os.environ.get("OLLAMA_MODEL")
    if ollama_model:
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        client = OpenAI(api_key="ollama", base_url=base_url)
        return client, ollama_model

    # Gemini via OpenAI compatibility
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        return client, model

    # OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        client = OpenAI(api_key=openai_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return client, model

    print("Error: No LLM provider configured.")
    print("Set one of these environment variables:")
    print("  $env:OLLAMA_MODEL='llama3'          (local Ollama, free)")
    print("  $env:GEMINI_API_KEY='your-key'      (Google Gemini)")
    print("  $env:OPENAI_API_KEY='your-key'      (OpenAI)")
    sys.exit(1)


def classify_complaint(client, model, row: dict) -> dict:
    """Classify a single complaint row using the LLM."""
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    user_prompt = f"""Classify this citizen complaint:

Complaint ID: {row.get('complaint_id', '')}
Location: {row.get('location', '')}
Description: {description}

Return ONLY a JSON object with category, priority, reason, flag."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )

    import json
    try:
        result = json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return valid JSON
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Classification failed — invalid LLM response",
            "flag": "NEEDS_REVIEW"
        }

    # Post-processing enforcement
    # Validate category
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    # Enforce severity keyword rule
    desc_lower = description.lower()
    has_severity = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    if has_severity and result.get("priority") != "Urgent":
        result["priority"] = "Urgent"
        result["reason"] = result.get("reason", "") + f" [Severity keyword detected]"

    result["complaint_id"] = row.get("complaint_id", "")
    return result


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    client, model = get_client_and_model()

    # Read input
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    required_cols = {"complaint_id", "description"}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        print(f"Error: Input CSV missing required columns: {required_cols}")
        sys.exit(1)

    print(f"[batch_classify] Processing {len(rows)} complaints...")

    results = []
    for i, row in enumerate(rows, 1):
        try:
            result = classify_complaint(client, model, row)
            results.append(result)
            print(f"  [{i}/{len(rows)}] {result['complaint_id']}: {result['category']} / {result['priority']}")
            # Rate limit: wait between API calls to avoid quota exhaustion
            if i < len(rows):
                time.sleep(5)
        except Exception as e:
            print(f"  [{i}/{len(rows)}] Error on {row.get('complaint_id', '?')}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW"
            })

    # Write output
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

    print(f"[done] Results written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
