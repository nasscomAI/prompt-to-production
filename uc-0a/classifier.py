"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os

try:
    from openai import OpenAI
    client = OpenAI()
except ImportError:
    client = None

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # Rule: If description is missing set flag: NEEDS_REVIEW and category: Other.
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW"
        }

    # If openai client is available, use it with the exact rules from agents.md
    if client is not None:
        prompt = f"""
        You are the City Services Complaint Classifier. Your boundary is the categorization and prioritization of municipal complaints based on text descriptions provided by citizens. You do not handle dispatch or resolution, only classification.
        
        Intent:
        A correct output is a JSON dictionary containing:
        1. category: Exactly one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other].
        2. priority: One of [Urgent, Standard, Low].
        3. reason: One sentence explanation of why the complaint is classified as such, Must cite specific words from description.
        4. flag: Set to "NEEDS_REVIEW" or blank. Set when category is genuinely ambiguous or leave blank.
        
        Context:
        You are NOT allowed to use any external data or assume conditions beyond what is explicitly stated in the description.
        
        Enforcement:
        - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - Priority must be Urgent if description contains words like injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
        - Every output row must include a reason field citing specific words from the description.
        
        Complaint to classify:
        {description}
        
        Output valid JSON only.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            result = json.loads(response.choices[0].message.content)
            
            return {
                "complaint_id": complaint_id,
                "category": result.get("category", "Other"),
                "priority": result.get("priority", "Low"),
                "reason": result.get("reason", "No reason provided."),
                "flag": result.get("flag", "")
            }
        except Exception as e:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": f"API Error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            }
            
    # Fallback to simple rule-based matching if no LLM client is available
    category = "Other"
    priority = "Standard"
    reason = "Automated fallback parsing."
    flag = ""
    
    desc_lower = str(description).lower()
    
    # Simple keyword matching for category
    categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"]
    for cat in categories:
        if cat.lower() in desc_lower:
            category = cat
            reason = f"Description contains '{cat.lower()}'."
            break
            
    # Simple keyword matching for priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    for word in urgent_keywords:
        if word in desc_lower:
            priority = "Urgent"
            reason += f" Flagged Urgent due to word '{word}'."
            break
            
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                classified = classify_complaint(row)
                results.append(classified)
    except Exception as e:
        print(f"Failed to read input CSV {input_path}: {e}")
        return

    if not results:
        print("No results generated.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output CSV {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
