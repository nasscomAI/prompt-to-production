"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import urllib.request
import urllib.error
import json
import re
import os

# API Configuration
K = "A_K"
URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS_TO_TRY = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.3-70b-specdec", "llama3-8b-8192"]

def ensure_single_sentence(reason: str) -> str:
    reason = reason.strip()
    if not reason:
        return ""
    # Split by sentence end markers (. ! ?) followed by whitespace or end of string
    sentences = re.split(r'(?<=[.!?])\s+', reason)
    if sentences:
        s = sentences[0].strip()
        # Ensure it ends with a period if it doesn't already have end punctuation
        if s and s[-1] not in ['.', '!', '?']:
            s += '.'
        return s
    return reason

def query_llm(system_prompt: str, user_prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {K}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    last_err = None
    for model in MODELS_TO_TRY:
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }
        
        req = urllib.request.Request(
            URL,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                res_data = response.read().decode("utf-8")
                res_json = json.loads(res_data)
                content = res_json["choices"][0]["message"]["content"]
                parsed_content = json.loads(content)
                return parsed_content
        except Exception as e:
            last_err = e
            print(f"Warning: Model {model} failed with error: {e}. Trying next model...")
            continue
            
    raise Exception(f"All models failed. Last error: {last_err}")

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # 1. Flag nulls/empty/invalid descriptions programmatically
    if not description or not str(description).strip() or str(description).lower() in ["null", "none"]:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided or description is null.",
            "flag": "NEEDS_REVIEW"
        }
        
    description = str(description).strip()
    
    # 2. Check severity keywords programmatically to guarantee 100% adherence
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    has_severity = False
    desc_lower = description.lower()
    for kw in severity_keywords:
        if kw in desc_lower:
            has_severity = True
            break
            
    system_prompt = (
        "You are an automated municipal civic complaint classifier. Your role is to classify a citizen's complaint into the appropriate category and priority, provide a one-sentence explanation, and flag it if it's ambiguous.\n\n"
        "Allowed categories (exact strings only):\n"
        "- Pothole\n"
        "- Flooding\n"
        "- Streetlight\n"
        "- Waste\n"
        "- Noise\n"
        "- Road Damage\n"
        "- Heritage Damage\n"
        "- Heat Hazard\n"
        "- Drain Blockage\n"
        "- Other\n\n"
        "Allowed priorities:\n"
        "- Urgent\n"
        "- Standard\n"
        "- Low\n\n"
        "Allowed flags:\n"
        "- NEEDS_REVIEW (use if category is ambiguous or description is unclear)\n"
        "- Leave empty string (\"\") if clear\n\n"
        "Reason requirements:\n"
        "- Must be exactly one sentence.\n"
        "- Must cite specific words from the complaint description.\n\n"
        "Refusal condition:\n"
        "- If the category cannot be confidently determined from the description alone, set category to 'Other' and flag to 'NEEDS_REVIEW'.\n\n"
        "You MUST respond ONLY with a JSON object containing the keys: \"category\", \"priority\", \"reason\", \"flag\". Do not include any other text."
    )
    
    user_prompt = f"Complaint ID: {complaint_id}\nDescription: {description}"
    
    try:
        parsed = query_llm(system_prompt, user_prompt)
        
        category = str(parsed.get("category", "")).strip()
        priority = str(parsed.get("priority", "")).strip()
        reason = str(parsed.get("reason", "")).strip()
        flag = str(parsed.get("flag", "")).strip()
        
        # Normalize category
        allowed_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
        category_map = {
            "pothole": "Pothole",
            "potholes": "Pothole",
            "flooding": "Flooding",
            "flood": "Flooding",
            "streetlight": "Streetlight",
            "streetlights": "Streetlight",
            "street light": "Streetlight",
            "street lights": "Streetlight",
            "waste": "Waste",
            "garbage": "Waste",
            "trash": "Waste",
            "noise": "Noise",
            "road damage": "Road Damage",
            "road": "Road Damage",
            "heritage damage": "Heritage Damage",
            "heritage": "Heritage Damage",
            "heat hazard": "Heat Hazard",
            "heat": "Heat Hazard",
            "drain blockage": "Drain Blockage",
            "drain": "Drain Blockage",
            "drainage": "Drain Blockage",
            "other": "Other"
        }
        
        normalized_cat = category_map.get(category.lower(), category)
        if normalized_cat not in allowed_categories:
            normalized_cat = "Other"
            flag = "NEEDS_REVIEW"
            
        # Normalize priority
        allowed_priorities = ["Urgent", "Standard", "Low"]
        normalized_prio = priority.title()
        if normalized_prio not in allowed_priorities:
            normalized_prio = "Standard"
            
        # Force urgent if severity keywords present
        if has_severity:
            normalized_prio = "Urgent"
            
        # Normalize flag
        if flag.upper() == "NEEDS_REVIEW":
            normalized_flag = "NEEDS_REVIEW"
        else:
            normalized_flag = ""
            
        # Normalize reason to single sentence
        normalized_reason = ensure_single_sentence(reason)
        
        return {
            "complaint_id": complaint_id,
            "category": normalized_cat,
            "priority": normalized_prio,
            "reason": normalized_reason,
            "flag": normalized_flag
        }
        
    except Exception as e:
        # Safe fallback on exceptions
        normalized_prio = "Urgent" if has_severity else "Standard"
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": normalized_prio,
            "reason": f"Fallback classification due to API error: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    except Exception as e:
        print(f"Error reading input CSV {input_path}: {e}")
        return
        
    print(f"Loaded {len(rows)} rows from {input_path}. Starting classification...")
    
    for i, row in enumerate(rows, start=1):
        try:
            print(f"[{i}/{len(rows)}] Classifying complaint {row.get('complaint_id', 'unknown')}...")
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            print(f"Unexpected error classifying row {i}: {e}")
            desc = row.get("description", "").lower()
            severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
            prio = "Urgent" if any(kw in desc for kw in severity_keywords) else "Standard"
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": prio,
                "reason": f"Unexpected classification failure: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Successfully wrote output to {output_path}")
    except Exception as e:
        print(f"Error writing output CSV {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
