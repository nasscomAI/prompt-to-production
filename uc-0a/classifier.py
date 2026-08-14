"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify using Claude API.
Enforces RICE rules from agents.md and skills.md.
"""
import argparse
import csv
import json
import logging
import os
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
VALID_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using Claude API.
    Input: dict with keys — id (str), description (str)
    Output: dict with keys — category (str), priority (str), reason (str), flag (str)
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("id", "unknown")

    if not description:
        logger.warning(f"Empty description for complaint {complaint_id}")
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient description to classify",
            "flag": "NEEDS_REVIEW"
        }

    try:
        client = Anthropic()

        prompt = f"""Classify this citizen complaint strictly. Output ONLY valid JSON with no markdown or extra text.

COMPLAINT: "{description}"

ENFORCEMENT RULES:
1. Category must be exactly one of: {', '.join(VALID_CATEGORIES)}
2. Priority = "Urgent" if description contains ANY of: {', '.join(SEVERITY_KEYWORDS)}. Otherwise "Standard" or "Low".
3. Reason: one sentence citing specific words from complaint.
4. Flag: "NEEDS_REVIEW" if category is ambiguous, else "" (empty string).
5. Do NOT hallucinate categories or apply external knowledge.

Output JSON only:
{{"category": "<category>", "priority": "<priority>", "reason": "<reason>", "flag": "<flag>"}}"""

        message = client.messages.create(
            model="claude-opus-5",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = ""
        for block in message.content:
            if hasattr(block, 'text'):
                response_text = block.text.strip()
                break

        if not response_text:
            raise ValueError("No text content in response")

        result = json.loads(response_text)

        if result.get("category") not in VALID_CATEGORIES:
            logger.warning(f"Invalid category '{result.get('category')}' for {complaint_id}, setting to Other")
            result["category"] = "Other"
            result["flag"] = "NEEDS_REVIEW"

        if result.get("priority") not in VALID_PRIORITIES:
            logger.warning(f"Invalid priority '{result.get('priority')}' for {complaint_id}, setting to Standard")
            result["priority"] = "Standard"

        return result

    except json.JSONDecodeError:
        logger.error(f"JSON decode error for {complaint_id}")
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Error parsing classification",
            "flag": "NEEDS_REVIEW"
        }
    except Exception as e:
        logger.error(f"Error classifying {complaint_id}: {str(e)}")
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Error during classification",
            "flag": "NEEDS_REVIEW"
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        logger.info(f"Read {len(rows)} complaints from {input_path}")
    except Exception as e:
        logger.error(f"Error reading input: {str(e)}")
        raise

    results = []
    for i, row in enumerate(rows, 1):
        try:
            classified = classify_complaint(row)
            result_row = {
                "id": row.get("id", f"row_{i}"),
                "description": row.get("description", ""),
                "category": classified["category"],
                "priority": classified["priority"],
                "reason": classified["reason"],
                "flag": classified["flag"]
            }
            results.append(result_row)
            logger.info(f"[{i}/{len(rows)}] {result_row['id']} → {result_row['category']} ({result_row['priority']})")
        except Exception as e:
            logger.warning(f"Row {i} failed: {str(e)}, flagging as NEEDS_REVIEW")
            result_row = {
                "id": row.get("id", f"row_{i}"),
                "description": row.get("description", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "Error during classification",
                "flag": "NEEDS_REVIEW"
            }
            results.append(result_row)

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "description", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"Results written to {output_path}")
    except IOError as e:
        logger.error(f"Error writing output: {str(e)}")
        raise IOError(f"Cannot write to {output_path}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
