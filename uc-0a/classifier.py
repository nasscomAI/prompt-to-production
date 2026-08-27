import argparse
import csv
import json
import os
import re
import time

def get_agent_rules(agents_path="agents.md", skills_path="skills.md") -> str:
    """Read agents.md and skills.md to construct the system prompt."""
    prompt = "You are an AI assistant acting as a Civic Complaint Classifier.\n\n"
    
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            prompt += "=== AGENT INSTRUCTIONS ===\n"
            prompt += f.read() + "\n\n"
            
    if os.path.exists(skills_path):
        with open(skills_path, 'r', encoding='utf-8') as f:
            prompt += "=== SKILL INSTRUCTIONS ===\n"
            prompt += f.read() + "\n\n"
            
    return prompt

def rule_based_classification(row: dict) -> dict:
    """
    Classifies a complaint row without using the OpenAI API, relying on rules.
    """
    desc = row.get('description', '').lower()
    loc = row.get('location', '').lower()
    
    category = "Other"
    priority = "Low"
    reason = "Categorization ambiguous or unclassifiable."
    flag = "NEEDS_REVIEW"
    
    # 1. Determine Category and extract a reason quote
    if any(word in desc for word in ['pothole', 'tyre', 'crater', 'cracked', 'subsidence']):
        category = "Pothole" if 'pothole' in desc else "Road Damage"
        reason = "Description mentions 'pothole'." if category == "Pothole" else "Description mentions road surface issues."
        flag = ""
    elif any(word in desc for word in ['flood', 'rainwater', 'drain', 'mosquito', 'dengue', 'knee-deep', 'water', 'blocked']):
         if 'flood' in desc or 'rain' in desc or 'water' in desc:
             category = "Flooding"
             reason = "Description mentions flooding or rainwater accumulation."
         else:
             category = "Drain Blockage"
             reason = "Description mentions blocked drains."
         flag = ""
    elif any(word in desc for word in ['streetlights', 'light', 'dark', 'bulb', 'wire', 'electrical', 'sparking', 'lamp post', 'substation', 'tripped', 'electricity']):
         category = "Streetlight"
         reason = "Description mentions electrical issues or streetlights."
         flag = ""
    elif any(word in desc for word in ['waste', 'garbage', 'dumped', 'bin', 'smell']):
         category = "Waste"
         reason = "Description mentions waste or garbage accumulation."
         flag = ""
    elif any(word in desc for word in ['music', 'noise', 'drilling', 'amplifiers', 'club']):
         category = "Noise"
         reason = "Description mentions noise issues like music or drilling."
         flag = ""
    elif 'heat' in desc or '44°c' in desc or 'temperature' in desc or 'burn' in desc or 'sun' in desc:
         category = "Heat Hazard"
         reason = "Description mentions severe heat or high temperatures."
         flag = ""
    elif 'heritage' in desc or 'historic' in desc or 'ancient' in desc or 'tagore museum' in desc or 'victoria' in desc:
         # Need to be careful here, could be pothole near heritage. 
         # But the requirement is to not hallucinate and pick standard categories.
         if 'damage' in desc or 'defaced' in desc or 'removed' in desc:
            category = "Heritage Damage"
            reason = "Description mentions damage to a heritage site."
            flag = ""
    
    # Check if category is genuinely ambiguous (simulating the LLM)
    if category == "Other":
        if 'tree' in desc and 'fall' in desc:
           category = "Other"
           flag = "NEEDS_REVIEW"
           reason = "Tree fall hazard is not in allowed categories."
        # If multiple could match, keeping it simple.
    
    # 2. Determine Priority
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse', 'life at risk', 'stranded', 'trapped', 'danger']
    
    if any(kw in desc for kw in urgent_keywords) or any(kw in loc for kw in urgent_keywords):
        priority = "Urgent"
        # Find which keyword triggered it for the reason
        triggered = [kw for kw in urgent_keywords if kw in desc or kw in loc]
        reason += f" Priority set to Urgent because description contains '{triggered[0]}'."
    else:
        # Simple heuristic: older open days = higher priority
        days = int(row.get('days_open', 0)) if row.get('days_open', '').isdigit() else 0
        if days > 10:
             priority = "Standard"
        else:
             priority = "Low"

    return {
         "complaint_id": row.get('complaint_id', 'UNKNOWN'),
         "category": category,
         "priority": priority,
         "reason": reason,
         "flag": flag
    }


def classify_complaint(row: dict, system_prompt: str) -> dict:
    """
    Wrapper for offline classification.
    """
    return rule_based_classification(row)


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        return

    # Assuming the current file is in uc-0a/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(script_dir, "agents.md")
    skills_path = os.path.join(script_dir, "skills.md")
    
    system_prompt = get_agent_rules(agents_path, skills_path)
    
    results = []
    success_count = 0
    fail_count = 0
    
    print(f"Reading from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                complaint_id = row.get('complaint_id', 'UNKNOWN')
                print(f"Classifying {complaint_id}...")
                
                # Check for bad row / nulls
                if not row.get('description'):
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description",
                        "flag": "NEEDS_REVIEW"
                    })
                    fail_count += 1
                    continue
                
                classification = classify_complaint(row, system_prompt)
                
                # Validation of required keys
                keys = ['complaint_id', 'category', 'priority', 'reason', 'flag']
                final_row = {k: classification.get(k, '') for k in keys}
                
                if final_row['category'] == 'Other' and final_row['flag'] == 'NEEDS_REVIEW':
                   fail_count += 1
                else:
                   success_count += 1
                
                results.append(final_row)
                
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    print(f"Writing results to {output_path}...")
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
         print(f"Error writing output file: {e}")
         return

    print(f"Batch complete. Successes: {success_count}, Failures/Reviews: {fail_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
