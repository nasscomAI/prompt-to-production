"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import json

# Try to import google.generativeai for LLM-based classification
HAS_GEMINI = False
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    pass

# Retrieve API keys and configure if available
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if HAS_GEMINI and api_key:
    genai.configure(api_key=api_key)
else:
    HAS_GEMINI = False


def classify_complaint_llm(row: dict) -> dict:
    """
    Calls the Gemini API using system instruction derived from agents.md.
    """
    complaint_id = row.get("complaint_id", "")
    desc = row.get("description", "").strip()
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description field.",
            "flag": "NEEDS_REVIEW"
        }
        
    system_instruction = (
        "You are a municipal citizen complaint classifier agent. Your operational boundary is strictly to classify incoming raw citizen complaints into standard municipal categories, assess their severity/priority based on safety-critical keywords, provide a brief cited justification, and flag ambiguous items.\n\n"
        "Rules:\n"
        "1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations allowed.\n"
        "2. Priority must be Urgent if the description contains (case-insensitive) any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. If none of these keywords are present, choose Standard or Low based on the description.\n"
        "3. Reason must be exactly one sentence and must cite specific words from the description to justify the category and priority.\n"
        "4. Refusal condition / Ambiguity: If the category is genuinely ambiguous or does not fit any existing category, classify category as 'Other' and set flag to 'NEEDS_REVIEW'. Otherwise, the flag must be empty.\n"
        "5. Output must be a JSON object with keys: category, priority, reason, flag."
    )
    
    prompt = f"Complaint Description:\n{desc}\n\nProvide the classification JSON:"
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction,
        generation_config={"response_mime_type": "application/json"}
    )
    
    response = model.generate_content(prompt)
    data = json.loads(response.text.strip())
    
    # Parse and clean response
    category = data.get("category", "Other")
    allowed_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    if category not in allowed_categories:
        matched = False
        for c in allowed_categories:
            if c.lower() == category.lower():
                category = c
                matched = True
                break
        if not matched:
            category = "Other"
            
    priority = data.get("priority", "Standard")
    if priority not in ["Urgent", "Standard", "Low"]:
        priority = "Standard"
        
    reason = data.get("reason", "")
    flag = data.get("flag", "")
    if flag not in ["NEEDS_REVIEW", ""]:
        flag = ""
        
    # Programmatic check for severity keyword override
    desc_lower = desc.lower()
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(kw in desc_lower for kw in severity_keywords):
        priority = "Urgent"
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def classify_complaint_rules(row: dict) -> dict:
    """
    Deterministic rule-based fallback classifier.
    Handles matching for standard municipal categories and enforces RICE rules.
    """
    complaint_id = row.get("complaint_id", "")
    desc = row.get("description", "").strip()
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description field.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = desc.lower()
    
    # Check severity keywords for priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    category = "Other"
    reason = ""
    flag = ""
    
    # Genuinely ambiguous check (heritage structures vs municipal infrastructure)
    is_heritage = "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower
    infra_terms = ["light", "lamp", "street", "road", "pave", "paving", "stone", "well", "substation"]
    
    # Ambiguous if mentioning heritage/historic/ancient and an infrastructure term
    # But NOT if it's explicitly about waste or noise (which are distinct issues)
    is_ambiguous = is_heritage and any(term in desc_lower for term in infra_terms) and not any(kw in desc_lower for kw in ["garbage", "waste", "music", "band", "amplifier"])
    
    if is_ambiguous:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Genuinely ambiguous category between Heritage and municipal infrastructure."
    elif "pothole" in desc_lower:
        category = "Pothole"
        reason = "Classified as Pothole citing description words: 'pothole'."
    elif "flood" in desc_lower or "waterlog" in desc_lower or "rain" in desc_lower:
        if "drain" in desc_lower:
            category = "Drain Blockage"
            reason = "Classified as Drain Blockage citing 'drain' and flooding/rain indicators."
        else:
            category = "Flooding"
            reason = "Classified as Flooding citing flooding/rain indicators."
    elif "drain" in desc_lower or "sewer" in desc_lower or "draining" in desc_lower:
        category = "Drain Blockage"
        reason = "Classified as Drain Blockage citing 'drain' or drainage words."
    elif "light" in desc_lower or "lamp" in desc_lower or "unlit" in desc_lower or "darkness" in desc_lower or "sparking" in desc_lower:
        category = "Streetlight"
        reason = "Classified as Streetlight citing lighting/darkness indicators."
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower or "bin" in desc_lower or "litter" in desc_lower:
        category = "Waste"
        reason = "Classified as Waste citing waste/garbage/litter words."
    elif "noise" in desc_lower or "music" in desc_lower or "loudspeaker" in desc_lower or "drilling" in desc_lower or "drill" in desc_lower or "amplifier" in desc_lower or "band" in desc_lower or "playing" in desc_lower:
        category = "Noise"
        reason = "Classified as Noise citing noise/music/playing words."
    elif "heat" in desc_lower or "melting" in desc_lower or "temperature" in desc_lower or "sun" in desc_lower or "hot" in desc_lower or "°c" in desc_lower:
        category = "Heat Hazard"
        reason = "Classified as Heat Hazard citing heat/temperature indicators."
    elif "road" in desc_lower or "surface" in desc_lower or "manhole" in desc_lower or "footpath" in desc_lower or "tile" in desc_lower or "crater" in desc_lower or "subsided" in desc_lower or "subsidence" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower or "paving" in desc_lower or "divider" in desc_lower:
        category = "Road Damage"
        reason = "Classified as Road Damage citing road/footpath/surface damage."
    elif is_heritage:
        category = "Heritage Damage"
        reason = "Classified as Heritage Damage citing heritage/historic/ancient keywords."
    else:
        category = "Other"
        reason = "Classified as Other since description does not match any primary category keywords."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }



def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if HAS_GEMINI:
        try:
            return classify_complaint_llm(row)
        except Exception as e:
            # Fail silently and fall back to the rule-based classifier
            return classify_complaint_rules(row)
    else:
        return classify_complaint_rules(row)


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, 1):
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as row_err:
                    complaint_id = row.get("complaint_id", f"UNKNOWN_{row_idx}")
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error classifying row: {str(row_err)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        raise
    except Exception as file_err:
        print(f"Error reading input file: {str(file_err)}")
        raise

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as write_err:
        print(f"Error writing to output file {output_path}: {str(write_err)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
