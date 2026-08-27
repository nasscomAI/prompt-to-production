"""
UC-0A — Complaint Classifier
Implements the skills defined in skills.md and enforces the taxonomy in agents.md.
"""
import argparse
import csv
import json
import os

def load_system_prompt() -> str:
    """Reads the RICE prompt directly from agents.md to ensure it is always up to date."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(current_dir, "agents.md")
    
    try:
        with open(agents_path, "r", encoding="utf-8") as f:
            prompt_content = f.read().strip()
            # Append JSON formatting enforcement for the model
            return prompt_content + "\n\nPlease output the evaluation STRICTLY as a JSON object with keys: 'category', 'priority', 'reason', and 'flag'."
    except FileNotFoundError:
        print(f"Warning: {agents_path} not found. Ensure it is correctly defined.")
        return "You are an expert complaint classifier. Please output JSON with category, priority, reason, flag."

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint description into an exact predefined category, 
    priority level, justification reason, and review flag based on agents.md rules.
    """
    description = str(row.get('description', '')).strip()
    
    if not description:
        row['category'] = 'Other'
        row['priority'] = 'Low'
        row['reason'] = 'The complaint description is completely empty.'
        row['flag'] = 'NEEDS_REVIEW'
        return row

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Fallback behaviour strictly enforcing exactly the agents.md rules deterministically
        desc_lower = description.lower()
        categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"]
        severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
        
        matched_cats = [c for c in categories if c.lower() in desc_lower]
        if "water" in desc_lower and "Flooding" not in matched_cats: matched_cats.append("Flooding")
        if "crack" in desc_lower and "Road Damage" not in matched_cats: matched_cats.append("Road Damage")
        
        category = matched_cats[0] if len(matched_cats) == 1 else "Other"
        flag = "NEEDS_REVIEW" if category == "Other" else ""
        
        urgent_kws = [kw for kw in severity_keywords if kw in desc_lower]
        priority = "Urgent" if urgent_kws else "Standard"
        
        if priority == "Urgent":
            reason = f"The description contains the severity keyword '{urgent_kws[0]}'."
        elif category != "Other":
            reason = f"The description mentions the specific issue mapped to {category}."
        else:
            reason = "The description is genuinely ambiguous and cannot be determined solely from the text."
            
        row['category'] = category
        row['priority'] = priority
        row['reason'] = reason
        row['flag'] = flag
        return row
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": load_system_prompt()},
                {"role": "user", "content": description}
            ],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        
        row['category'] = result.get('category', 'Other')
        row['priority'] = result.get('priority', 'Standard')
        row['reason'] = result.get('reason', 'Missing reason field.')
        row['flag'] = result.get('flag', '')

        # Enforce valid category fallback to avoid taxonomy drift
        valid_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
        if row['category'] not in valid_categories:
            row['category'] = 'Other'
            row['flag'] = 'NEEDS_REVIEW'

        # Ensure flag is entirely blank if not NEEDS_REVIEW
        if row['flag'] != 'NEEDS_REVIEW':
            row['flag'] = ''
            
    except Exception as e:
        row['category'] = 'Other'
        row['priority'] = 'Low'
        row['reason'] = f'Error processing with AI Tool: {str(e)}'
        row['flag'] = 'NEEDS_REVIEW'
        
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV file of citizen complaints, iteratively applies classify_complaint 
    to each row, and writes the results to an output CSV file.
    Gracefully skips completely empty rows as specified in skills.md.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            
            # Ensure our newly generated keys exist in the output
            for key in ["category", "priority", "reason", "flag"]:
                if key not in fieldnames:
                    fieldnames.append(key)
                    
            for row in reader:
                # Skill: Gracefully skip completely empty rows instead of halting
                if not any(val.strip() if isinstance(val, str) else val for val in row.values() if val):
                    continue
                results.append(classify_complaint(row))
                
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        return
        
    # Write the batch results
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not found in environment. Using deterministic fallback classifier.")
        
    print(f"Processing {args.input}...")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
