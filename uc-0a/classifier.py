"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_system_prompt() -> str:
    # Read agents.md as the core prompt rules
    prompt = "You are a civic tech classification agent.\n\n"
    agents_path = os.path.join(os.path.dirname(__file__), "agents.md")
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            prompt += f.read()
            
    prompt += "\n\nRespond ONLY with a valid JSON object containing exactly the following keys: \"category\", \"priority\", \"reason\", and \"flag\"."
    return prompt

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    
    system_prompt = get_system_prompt()
    user_prompt = f"Please classify the following complaint description:\n\n{description}"
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result_json = response.choices[0].message.content
        result_dict = json.loads(result_json)
        
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": result_dict.get("category", "Other"),
            "priority": result_dict.get("priority", "Standard"),
            "reason": result_dict.get("reason", ""),
            "flag": result_dict.get("flag", "")
        }
    except Exception as e:
        print(f"Error classifying row {row.get('complaint_id')}: {e}")
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": f"Error: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"Processing {row.get('complaint_id')}...")
            classified = classify_complaint(row)
            results.append(classified)
            
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
