import argparse
import csv
import sys
import os
import json

def parse_simple_yaml(filepath: str) -> dict:
    """Basic YAML parser for simple key-value and list structures."""
    config = {"enforcement": []}
    with open(filepath, "r", encoding="utf-8") as f:
        for auto_line in f:
            line = auto_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- "):
                rule = line[2:].strip("\"' ")
                config["enforcement"].append(rule)
            elif ":" in auto_line:
                key, val = auto_line.split(":", 1)
                key = key.strip()
                val = val.strip().strip("\"' ")
                if key and key != "enforcement":
                    config[key] = val
    return config

def get_system_prompt() -> str:
    """Constructs the system prompt from the agents.md file restrictions."""
    agent_path = os.path.join(os.path.dirname(__file__), "agents.md")
    try:
        agent_config = parse_simple_yaml(agent_path)
    except FileNotFoundError:
        return "You are a fallback civic complaint classifier. Follow rules strictly."
    
    role = agent_config.get("role", "Complaint Classification Agent")
    intent = agent_config.get("intent", "Classify incoming complaints strictly.")
    context = agent_config.get("context", "")
    enforcement_list = agent_config.get("enforcement", [])
    enforcement_text = "\n".join([f"- {rule}" for rule in enforcement_list])
    
    return f"ROLE: {role}\nINTENT: {intent}\nCONTEXT: {context}\nENFORCEMENT RULES:\n{enforcement_text}\n\nYou must strictly adhere to all enforcement rules. Provide your response as valid JSON with no markdown wrapping, and ONLY use keys: 'category', 'priority', 'reason', and 'flag'."

# Establish LLM capabilities dynamically based on environment keys
SYSTEM_PROMPT = get_system_prompt()
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

client = None
if OPENAI_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
    except ImportError:
        print("OpenAI key found but library not installed.")

gemini_model = None
if GEMINI_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
    except ImportError:
        print("Gemini key found but library not installed.")


def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Low",
        "reason": "Default handling due to unspecified error or blank description.",
        "flag": "NEEDS_REVIEW"
    }

    if not desc:
        return result

    user_prompt = f"Classify this complaint description: '{desc}'"

    try:
        raw_json = None
        if client:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            raw_json = response.choices[0].message.content
        elif gemini_model:
            response = gemini_model.generate_content(user_prompt)
            raw_json = response.text
        else:
            return fallback_classify(row)
        
        # Clean JSON markdown if LLM includes it
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3]
        elif raw_json.startswith("```"):
            raw_json = raw_json[3:-3]
        
        parsed = json.loads(raw_json.strip())
        
        result["category"] = parsed.get("category", "Other")
        result["priority"] = parsed.get("priority", "Low")
        result["reason"] = parsed.get("reason", "No reason provided")
        result["flag"] = parsed.get("flag", "")
        
    except Exception as e:
        print(f"Error classifying complaint {complaint_id}: {e}")
        # Default flags persist
        pass

    return result


def fallback_classify(row: dict) -> dict:
    """Skill: classify_complaint (Fallback Mode)"""
    desc = row.get("description", "").lower()
    
    # Priority logic
    urgents = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Urgent" if any(u in desc for u in urgents) else "Standard"

    # Category matching logic
    cat = "Other"
    categories = {
        "Pothole": ["pothole"], 
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "dark", "light", "sparking"],
        "Waste": ["garbage", "waste", "bin", "dump"],
        "Noise": ["music", "loud", "noise"],
        "Road Damage": ["crack", "road surface", "broken"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "drainage", "manhole"]
    }
    
    for real_cat, keywords in categories.items():
        if any(k in desc for k in keywords):
            cat = real_cat
            break
            
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": cat,
        "priority": priority,
        "reason": f"Fallback heuristic match on keywords.",
        "flag": "" if cat != "Other" else "NEEDS_REVIEW"
    }


def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify / save_results
    Read input CSV, classify each row, and write to results CSV.
    Must flag nulls, not crash on bad rows, and ensure output is saved.
    """
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as in_csv:
            reader = csv.DictReader(in_csv)
            for i, row in enumerate(reader):
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as row_error:
                    print(f"Skipping badly malformed row {i+1}: {row_error}")
                    continue
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        sys.exit(1)
        
    # Write Out (Skill: save_results)
    try:
        with open(output_path, mode="w", encoding="utf-8", newline='') as out_csv:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except IOError as e:
        print(f"Failed to write output to {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        print("WARNING: No LLM API key detected. Running fallback regex classifier...")
        
    batch_classify(args.input, args.output)
    print(f"Done. Results safely written to {args.output}")
