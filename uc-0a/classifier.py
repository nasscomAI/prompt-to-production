"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import time
import json
from google import genai
from google.genai import errors
from dotenv import load_dotenv

# Load API key from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}


def classify_complaint(row: dict) -> dict:
    """
    ENFORCED VERSION — uses structured JSON output from the LLM, then
    applies hard-coded rules from agents.md regardless of what the model says.
    """
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "")

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    prompt = f"""Classify this citizen complaint. Respond with ONLY valid JSON, no markdown, no extra text.

Allowed categories (choose exactly one, verbatim): {", ".join(sorted(ALLOWED_CATEGORIES))}

JSON format:
{{"category": "...", "priority": "Urgent|Standard|Low", "reason": "one sentence citing specific words from the description"}}

Complaint: {description}"""

    max_retries = 5
    parsed = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").replace("json", "", 1).strip()
            parsed = json.loads(raw)
            break
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries - 1:
                wait = 10 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise
        except (json.JSONDecodeError, AttributeError):
            parsed = None
            break

    if not parsed:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Model output could not be parsed",
            "flag": "NEEDS_REVIEW"
        }

    category = parsed.get("category", "").strip()
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        flag = parsed.get("flag", "") or ""

    reason = parsed.get("reason", "").strip() or "No justification provided"

    desc_lower = description.lower()
    if any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = parsed.get("priority", "Standard")
        if priority not in {"Urgent", "Standard", "Low"}:
            priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for i, row in enumerate(rows):
        result = classify_complaint(row)
        results.append(result)
        print(f"Classified {i+1}/{len(rows)}")
        time.sleep(3)  # pace requests to stay under rate limit

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")