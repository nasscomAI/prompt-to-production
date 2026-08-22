"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import time
from google import genai
from google.genai import errors
from dotenv import load_dotenv

# Load API key from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def classify_complaint(row: dict) -> dict:
    """
    NAIVE VERSION — deliberately weak, no enforcement yet.
    This is meant to show the failure modes described in agents.md.
    """
    description = row.get("description", "")
    prompt = f"Classify this citizen complaint by category and priority.\n\nComplaint: {description}"

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return {
                "complaint_id": row.get("complaint_id", ""),
                "category": response.text,
                "priority": "",
                "reason": "",
                "flag": ""
            }
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries - 1:
                wait = 10 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise


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