import os
import csv
import argparse
import json
from openai import OpenAI

def parse_args():
    parser = argparse.ArgumentParser(description="UC-0A: Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to output results_[city].csv")
    return parser.parse_args()

def check_severity_keywords(description):
    """
    Hard-coded guardrail to prevent Severity Blindness. 
    Triggers 'Urgent' if any safety keywords are present.
    """
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    desc_lower = description.lower()
    for keyword in severity_keywords:
        if keyword in desc_lower:
            return True, keyword
    return False, None

def classify_complaint(client, description):
    """
    Analyzes a single citizen complaint text and returns a structured classification.
    """
    allowed_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
                          "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    
    # Pre-check for Urgent keywords (Failsafe against Severity Blindness)
    has_urgent_keyword, matched_word = check_severity_keywords(description)

    system_prompt = f"""You are an Urban Governance Analyst. Classify the citizen complaint provided by the user.
You MUST respond with a JSON object containing exactly four keys: "category", "priority", "reason", "flag".

Rules:
1. "category": Must be EXACTLY one of these strings: {", ".join(allowed_categories)}. Do not invent sub-categories or change casing.
2. "priority": If not already overridden, classify as "Urgent", "Standard", or "Low". 
3. "reason": Exactly ONE sentence justifying the category. You MUST explicitly cite or quote specific words from the text.
4. "flag": If the text is genuinely ambiguous, vague, or maps to multiple categories equally, set this to "NEEDS_REVIEW". Otherwise, leave it as an empty string "".

Your response must be valid raw JSON only."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Complaint text: {description}"}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Clean up taxonomy variations post-LLM
        category = result.get("category", "Other").strip()
        if category not in allowed_categories:
            category = "Other"

        priority = result.get("priority", "Standard").strip()
        if has_urgent_keyword:
            priority = "Urgent"
            
        reason = result.get("reason", "Classified based on operational criteria.").strip()
        flag = result.get("flag", "").strip()
        
        return category, priority, reason, flag

    except Exception as e:
        if has_urgent_keyword:
            return "Other", "Urgent", f"Failsafe triggered. Found urgent keyword '{matched_word}'.", "NEEDS_REVIEW"
        return "Other", "Standard", "Fallback classification due to system error.", "NEEDS_REVIEW"

def batch_classify(input_path, output_path):
    """
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    client = OpenAI() # Picks up OPENAI_API_KEY environment variable

    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        return

    # Read records
    rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Make sure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each row
    updated_rows = []
    for idx, row in enumerate(rows, 1):
        text = row.get("description", "") or row.get("complaint_text", "")
        
        print(f"Processing row {idx}/{len(rows)}...")
        category, priority, reason, flag = classify_complaint(client, text)
        
        # Mapping to required assignment schema columns
        row["category"] = category
        row["priority_flag"] = priority 
        row["reason"] = reason
        row["flag"] = flag
        
        updated_rows.append(row)

    if not updated_rows:
        print("No data processed.")
        return

    # Write out data
    new_headers = list(updated_rows[0].keys())
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_headers)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Successfully processed {len(updated_rows)} rows. Saved to: {output_path}")

def main():
    args = parse_args()
    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()