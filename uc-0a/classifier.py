"""
UC-0A — Complaint Classifier
Build this using the RICE -> agents.md -> skills.md workflow.
"""
import argparse
import csv
import os
import sys

# Attempt to load genai, but provide a graceful fallback.
try:
    from google import genai
    from pydantic import BaseModel, Field
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_system_instruction() -> str:
    """Read agents.md to act as the RICE system instruction."""
    agent_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agent_path):
        with open(agent_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Fallback prompt if agents.md not found: Classify complaints exactly as requested."

def classify_complaint_llm(row: dict, client) -> dict:
    """Use Gemini with Structured Outputs to classify the complaint."""
    description = row.get('description', '')
    sys_inst = get_system_instruction()

    class ComplaintResult(BaseModel):
        category: str = Field(description="Must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other")
        priority: str = Field(description="Urgent, Standard, or Low")
        reason: str = Field(description="One sentence citing specific words")
        flag: str = Field(description="NEEDS_REVIEW or blank")

    # Assuming gemini-2.5-flash is available
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=description,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ComplaintResult,
            'system_instruction': sys_inst,
            'temperature': 0.0,
        },
    )
    result_dict = response.parsed
    # merge with original row
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": result_dict.category if hasattr(result_dict, 'category') else "Other",
        "priority": result_dict.priority if hasattr(result_dict, 'priority') else "Low",
        "reason": result_dict.reason if hasattr(result_dict, 'reason') else "Failed to parse",
        "flag": result_dict.flag if hasattr(result_dict, 'flag') else "NEEDS_REVIEW"
    }

def classify_complaint_rule_based(row: dict) -> dict:
    """Fallback rule-based logic to perfectly emulate the RICE instructions if API fails/missing."""
    desc = row.get("description", "").lower()
    
    # Priority enforcement
    sev_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Urgent" if any(k in desc for k in sev_keywords) else "Standard"

    # Category enforcement
    category = "Other"
    if "pothole" in desc: category = "Pothole"
    elif "flood" in desc or "rain" in desc: category = "Flooding"
    elif "streetlight" in desc or "light" in desc: category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "dead animal" in desc: category = "Waste"
    elif "noise" in desc or "music" in desc: category = "Noise"
    elif "surface" in desc or "footpath" in desc: category = "Road Damage"
    elif "heritage" in desc: category = "Heritage Damage"
    elif "heat" in desc: category = "Heat Hazard"
    elif "drain" in desc or "manhole" in desc: category = "Drain Blockage"
    
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    reason = "No context reason."
    if category != "Other":
        matched_words = [w for w in desc.split() if w in ["pothole", "flood", "light", "waste", "noise"]]
        matched_word = matched_words[0] if matched_words else category
        reason = f"Description mentioned '{matched_word}' and other details."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def classify_complaint(row: dict, client=None) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if client:
        try:
            return classify_complaint_llm(row, client)
        except Exception as e:
            row["flag"] = "NEEDS_REVIEW"
            row["reason"] = f"LLM Error: {str(e)}"
            row["category"] = "Other"
            row["priority"] = "Low"
            return row
    return classify_complaint_rule_based(row)

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    client = None
    if HAS_GENAI and os.environ.get("GEMINI_API_KEY"):
        client = genai.Client()
        print("Using Gemini API for structured classification...")
    else:
        print("No GEMINI_API_KEY found or google-genai not installed. Using fallback rule-based classification.")
        print("Ensure you run 'pip install google-genai pydantic' and set GEMINI_API_KEY to use the AI tool.")

    if not os.path.exists(input_path):
        print(f"Error: Output path missing {input_path}")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Output CSV needs original complaint_id plus the 4 new metrics
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    results = []
    for i, row in enumerate(rows):
        print(f"Processing row {i+1}/{len(rows)}...")
        res = classify_complaint(row, client)
        
        results.append({
            "complaint_id": row.get("complaint_id", f"Row-{i}"),
            "category": res.get("category", "Other"),
            "priority": res.get("priority", "Low"),
            "reason": res.get("reason", ""),
            "flag": res.get("flag", "")
        })

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
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

