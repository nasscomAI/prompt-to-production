"""
UC-0A — Complaint Classifier
Uses gpt-4o with structured output (Pydantic) to enforce the classification schema.
Reads OPENAI_API_KEY from .env file in the project root.
"""
import argparse
import csv
import os
import time
from pathlib import Path
from typing import Literal

import certifi
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# Load .env from project root (one level up from uc-0a/)
load_dotenv(Path(__file__).parent.parent / ".env")

# Fix broken SSL_CERT_FILE env var (common in Anaconda envs on Windows)
os.environ["SSL_CERT_FILE"] = certifi.where()

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

SYSTEM_PROMPT = """You are a municipal complaint classifier for an Indian city government system.
Your only job is to read citizen complaint descriptions and assign a category, priority, reason, and review flag.
You do not solve complaints, suggest fixes, or add information beyond what is in the description.

Classification rules — enforce strictly:
- category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
- priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard; use Low only for complaints with no immediate impact
- reason must be one sentence that cites specific words or phrases from the description — no generic reasons
- flag must be NEEDS_REVIEW if the correct category cannot be determined from the description alone; otherwise leave it as an empty string
- Base classification solely on the description field — do not use location, ward, or reporter type"""


class Classification(BaseModel):
    category: Literal[
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    priority: Literal["Urgent", "Standard", "Low"]
    reason: str
    flag: Literal["NEEDS_REVIEW", ""]


client = OpenAI()


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this complaint:\n\nDescription: {description}"}
        ],
        response_format=Classification,
    )

    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError(f"Structured output parsing failed for complaint {complaint_id}")

    # Hard-enforce severity keyword rule regardless of what the model returned
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = result.priority

    return {
        "complaint_id": complaint_id,
        "category": result.category,
        "priority": priority,
        "reason": result.reason,
        "flag": result.flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Skips rows that fail, logs errors, still writes output for successful rows.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    needs_review_count = 0

    for row in rows:
        complaint_id = row.get("complaint_id", "UNKNOWN")
        for attempt in range(3):
            try:
                time.sleep(2)
                classification = classify_complaint(row)
                results.append(classification)
                if classification["flag"] == "NEEDS_REVIEW":
                    needs_review_count += 1
                print(f"  [{classification['priority']:8s}] {complaint_id}: {classification['category']}"
                      + (" [NEEDS_REVIEW]" if classification["flag"] else ""))
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  [RETRY {attempt+1}] {complaint_id}: {e}")
                    time.sleep(5)
                else:
                    print(f"  [ERROR] {complaint_id}: {e}")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nProcessed {len(results)}/{len(rows)} rows. "
          f"{needs_review_count} flagged NEEDS_REVIEW. "
          f"Results written to {output_path}")
    return len(results), needs_review_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)





