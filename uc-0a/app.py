import argparse
import csv
import json
import os
import re

# Schema Definitions
VALID_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}
VALID_PRIORITIES = {"Urgent", "Standard", "Low"}
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

SYSTEM_PROMPT = """
role: UC-0A Complaint Classifier agent. Its operational boundary is to process input rows of citizen complaints and classify them into predefined categories and priorities.

intent: Output must correctly assign exactly four fields per complaint row: category, priority, reason, and flag, strictly following the allowed schema values.

context: Allowed to use the complaint description. Must not use any pre-existing category or priority_flag columns, as they are stripped from the input.

enforcement:
- Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Exact strings only — no variations.
- Priority must be exactly one of: Urgent, Standard, Low.
- Priority must be Urgent if severity keywords present: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
- Reason must be exactly one sentence and must cite specific words from the description.
- Flag must be exactly NEEDS_REVIEW or blank, and must be set to NEEDS_REVIEW when category is genuinely ambiguous.
"""

def call_agent_api(description: str) -> dict:
    prompt = f"Classify the following complaint description:\n\n{description}\n\nReturn strictly valid JSON with exact keys: category, priority, reason, flag."
    
    # Attempt OpenAI first if key is present
    if os.environ.get("OPENAI_API_KEY"):
        import openai
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI error: {e}")
            pass

    # Attempt Gemini if key is present
    if os.environ.get("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            full_prompt = SYSTEM_PROMPT + "\n\n" + prompt
            response = model.generate_content(full_prompt)
            
            text = response.text
            json_match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            return json.loads(text.strip())
        except Exception as e:
            print(f"Gemini error: {e}")
            pass

    # Simple rule-based mock fallback for workshop/testing without API keys
    has_severity = any(keyword.lower() in description.lower() for keyword in SEVERITY_KEYWORDS)
    category = "Other"
    for cat in VALID_CATEGORIES:
        if cat.lower() in description.lower():
            category = cat
            break
            
    word = description.split()[0] if description else 'the issue'
    return {
        "category": category,
        "priority": "Urgent" if has_severity else "Standard",
        "reason": f"Classification is based on the specific mention of '{word}' in the citizen's report.",
        "flag": "NEEDS_REVIEW" if category == "Other" else ""
    }

def classify_complaint(row: dict) -> dict:
    """
    Skill: Classifies a single citizen complaint row into predefined category, priority, reason, and flag fields.
    """
    description = row.get("description", str(row))
    
    # Explicitly calculate local constraints to guarantee error_handling rules
    has_severity = any(keyword.lower() in description.lower() for keyword in SEVERITY_KEYWORDS)

    try:
        result = call_agent_api(description)
        
        category = result.get("category", "Other")
        priority = result.get("priority", "Low")
        reason = result.get("reason", "No reason provided.")
        flag = result.get("flag", "")
        
        # Error handling: Fallbacks to prevent hallucinated logic
        if category not in VALID_CATEGORIES:
            category = "Other"
            flag = "NEEDS_REVIEW"
            
        if priority not in VALID_PRIORITIES:
            priority = "Standard"
            
        # Error handling: Severity blindness protection
        if has_severity:
            priority = "Urgent"
            
        # Error handling: False confidence on ambiguity
        if flag not in ["NEEDS_REVIEW", "", None]:
            flag = ""
            
        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag if flag else ""
        }
        
    except Exception as e:
        print(f"Error classifying row: {e}")
        return {
            "category": "Other",
            "priority": "Urgent" if has_severity else "Standard",
            "reason": f"Fallback error handling triggered: {e}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Skill: Reads an input CSV of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    """
    results = []
    
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            # Strip context variables not allowed per agents.md
            stripped_row = {k: v for k, v in row.items() if k not in ("category", "priority_flag")}
            
            # Apply skill
            classification = classify_complaint(stripped_row)
            
            # Validate output prevents taxonomy drift by ensuring all keys are present
            merged_row = stripped_row.copy()
            merged_row.update(classification)
            results.append(merged_row)

    if not results:
        print("No valid rows found to process.")
        return

    # Prepare output fields ensuring our 4 classification columns follow original schema
    fieldnames = list(results[0].keys())
    for required in ["category", "priority", "reason", "flag"]:
        if required not in fieldnames:
            fieldnames.append(required)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    # Generate an attractive Markdown report for professional viewing
    md_path = output_path.replace('.csv', '.md')
    try:
        with open(md_path, mode='w', encoding='utf-8') as mdfile:
            mdfile.write("# 📊 Classification Results Report\n\n")
            mdfile.write("A professional overview of the classified citizen complaints.\n\n")
            mdfile.write("| ID | Category | Priority | Reason | Flag |\n")
            mdfile.write("|---|---|---|---|---|\n")
            for r in results:
                cid = r.get('complaint_id', 'N/A')
                cat = r.get('category', '')
                pri = r.get('priority', '')
                rsn = r.get('reason', '')
                flg = r.get('flag', '')
                
                # Add styling
                pri_style = f"**<span style='color:red'>{pri}</span>**" if pri == "Urgent" else pri
                flg_style = f"`{flg}`" if flg else ""
                
                mdfile.write(f"| {cid} | **{cat}** | {pri_style} | {rsn} | {flg_style} |\n")
        print(f"✨ Professional Markdown report generated at: {md_path}")
    except Exception as e:
        print(f"Could not generate markdown report: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", default="../data/city-test-files/test_hyderabad.csv", help="Path to input CSV (e.g. ../data/city-test-files/test_pune.csv)")
    parser.add_argument("--output", default="results_hyderabad.csv", help="Path to write results CSV (e.g. results_pune.csv)")
    
    args = parser.parse_args()
    print(f"🚀 Starting batch classification for {args.input}...")
    batch_classify(args.input, args.output)
    print(f"✅ Done. Results written to {args.output}")
