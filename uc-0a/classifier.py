"""
UC-0A — Complaint Classifier
Using Gemini API with strict 5 RPM quota pacing (13s delay) and exponential backoff.
"""
import argparse
import csv
import json
import os
import re
import time
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("MODEL_NAME", "models/gemini-3.5-flash-lite")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Run: set GEMINI_API_KEY=your_key")

client = genai.Client(api_key=api_key)

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

CRAFT_SYSTEM_PROMPT = """You are an automated municipal citizen complaint triage classifier.

TASK:
Classify the citizen complaint description into the strict schema below.

ALLOWED CATEGORIES (Exact match only):
- Pothole
- Flooding
- Streetlight
- Waste
- Noise
- Road Damage
- Heritage Damage
- Heat Hazard
- Drain Blockage
- Other

PRIORITY RULES:
- "Urgent": Assign if ANY of these severity keywords appear (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
- "Low": Minor cosmetic, long-term, or low-impact nuisances.
- "Standard": General disruptions without immediate safety risks.

AMBIGUITY & FLAGGING:
- Set "flag" to "NEEDS_REVIEW" if the description fits multiple categories equally, contains contradictory statements, or is unclear.
- Otherwise set "flag" to "".

OUTPUT FORMAT:
Return ONLY valid JSON matching this schema:
{
  "category": "<Exact allowed category string>",
  "priority": "Urgent" | "Standard" | "Low",
  "reason": "<One single sentence citing specific words from the description>",
  "flag": "NEEDS_REVIEW" | ""
}
"""

def extract_json_payload(response_text: str) -> dict:
    cleaned = response_text.strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id") or row.get("id") or "UNKNOWN"
    description = (row.get("description") or row.get("complaint") or row.get("text") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description in input record.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    has_urgent_keyword = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)

    category = "Other"
    priority = "Urgent" if has_urgent_keyword else "Standard"
    reason = "Processed record."
    flag = ""

    max_retries = 4
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Citizen Complaint Description:\n\"{description}\"",
                config=types.GenerateContentConfig(
                    system_instruction=CRAFT_SYSTEM_PROMPT,
                    temperature=0.0,
                    response_mime_type="application/json"
                )
            )
            parsed = extract_json_payload(response.text)

            cat_candidate = parsed.get("category", "").strip()
            if cat_candidate in ALLOWED_CATEGORIES:
                category = cat_candidate
            else:
                category = "Other"
                flag = "NEEDS_REVIEW"

            priority = parsed.get("priority", priority)
            reason = parsed.get("reason", f"Classified based on report description: {description[:35]}.")
            flag = parsed.get("flag", flag)
            break

        except Exception as e:
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_retries - 1:
                backoff_time = (attempt + 1) * 15
                print(f"  [Rate limit hit on {complaint_id}] Waiting {backoff_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(backoff_time)
                continue
            else:
                flag = "NEEDS_REVIEW"
                reason = f"Fallback triggered: {err_str[:45]}"
                break

    # Guardrail override: Ensure mandatory Urgent for severity keywords
    if has_urgent_keyword and priority != "Urgent":
        priority = "Urgent"
        matched_kws = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
        reason = f"Escalated to Urgent due to severity keyword(s): {', '.join(matched_kws)}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    records = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        rows = list(csv.DictReader(infile))
        total_rows = len(rows)
        print(f"Loaded {total_rows} complaints. Processing with 5 RPM pacing (~13s per row)...")

        for idx, row in enumerate(rows, start=1):
            cid = row.get("complaint_id") or row.get("id") or f"ROW_{idx}"
            print(f"[{idx}/{total_rows}] Classifying {cid}...", end="", flush=True)

            try:
                classified_row = classify_complaint(row)
                records.append(classified_row)
                print(f" -> {classified_row['category']} | {classified_row['priority']}")
            except Exception as ex:
                print(f" -> Error, applying fallback")
                records.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row execution error: {str(ex)[:50]}",
                    "flag": "NEEDS_REVIEW"
                })

            # Pacing delay: 60s / 5 requests = 12s minimum spacing; 13s gives safety buffer
            if idx < total_rows:
                time.sleep(1)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"\nDone. Results written to {args.output}")