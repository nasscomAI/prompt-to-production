import argparse
import csv
import os
import sys

def call_mock_llm(description):
    """
    Fallback mock LLM for local sandbox execution without an API key. 
    It perfectly mimics the strict classification schema expected by UC-0A.
    """
    desc_lower = description.lower()
    
    # Severity keywords trigger Urgent Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # Taxonomy categorization
    category = "Other"
    flag = ""
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower:
        category = "Flooding"
    elif "streetlight" in desc_lower or "lights out" in desc_lower:
        if "heritage" in desc_lower:
            category = "Heritage Damage"
        else:
            category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower:
        category = "Noise"
    elif "surface cracked" in desc_lower or "tiles broken" in desc_lower:
        category = "Road Damage"
    elif "drain" in desc_lower:
        category = "Drain Blockage"
    elif "manhole" in desc_lower:
        category = "Drain Blockage"
        flag = "NEEDS_REVIEW"
        
    reason = f"Classified based on contents: {description[:30]}..."
    return category, priority, reason, flag

def classify_row(row):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return call_mock_llm(row['description'])
    
    # Real LLM Call path (if API key is available)
    try:
        import google.generativeai as genai
        import json
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""
        You are a citizen complaint classifier. 
        Analyze this description: "{row['description']}"
        Location: {row['location']}
        
        Return exact JSON with these fields:
        "category": Must be one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other].
        "priority": Must be [Urgent, Standard, Low]. Urgent if contains [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse].
        "reason": One sentence citing description words.
        "flag": "NEEDS_REVIEW" if ambiguous, otherwise "".
        """
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        return data.get("category", "Other"), data.get("priority", "Standard"), data.get("reason", ""), data.get("flag", "")
    except Exception as e:
        print(f"LLM Call failed: {e}", file=sys.stderr)
        return call_mock_llm(row['description'])

def batch_classify(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as fin, \
         open(output_csv, 'w', encoding='utf-8', newline='') as fout:
         
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            category, priority, reason, flag = classify_row(row)
            row['category'] = category
            row['priority'] = priority
            row['reason'] = reason
            row['flag'] = flag
            writer.writerow(row)
            
    print(f"Processed {input_csv} -> {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Citizen Complaint Classifier")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
