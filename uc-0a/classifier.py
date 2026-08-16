"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import sys

def classify_complaint(client, prompt_base, row: dict) -> dict:
    prompt = f"{prompt_base}\n\nComplaint to classify:\n{json.dumps(row)}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    try:
        # Assuming the model returns JSON
        import re
        json_str = response.text
        match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if match:
            json_str = match.group(0)
        res = json.loads(json_str)
        return {
            "category": res.get("category", "Other"),
            "priority": res.get("priority", "Low"),
            "reason": res.get("reason", "No reason provided"),
            "flag": res.get("flag", "")
        }
    except Exception:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Failed to parse response",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
    except ImportError:
        print("Error: google-genai library is not installed.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    agents_md_path = os.path.join(os.path.dirname(__file__), "agents.md")
    with open(agents_md_path, "r", encoding="utf-8") as f:
        agents_content = f.read()

    prompt_base = f"Act as defined by:\n{agents_content}\n\nOutput ONLY raw JSON format with keys 'category', 'priority', 'reason', 'flag'."

    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        for row in reader:
            classification = classify_complaint(client, prompt_base, row)
            row.update(classification)
            results.append(row)

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
