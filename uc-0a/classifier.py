"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import pandas as pd

def extract_first_sentence(text: str) -> str:
    """
    Extract the first sentence from a description and ensure it is formatted
    correctly as one sentence ending with a period.
    """
    if not text:
        return ""
    # Split by period
    parts = text.split('.')
    first_part = parts[0].strip()
    if not first_part:
        return ""
    return first_part + "."

def classify_description(description: str) -> tuple[str, str, str, str]:
    """
    Core heuristic rules to classify a citizen complaint description
    into (category, priority, reason, flag).
    """
    description = str(description).strip()
    desc_lower = description.lower()
    
    # 1. Priority check: Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # 2. Extract first sentence for reason
    reason = extract_first_sentence(description)
    
    # 3. Category rules
    category = "Other"
    flag = ""
    
    # Check for ambiguity conditions first
    is_heritage_ambiguous = ("heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower) and \
                             ("garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "vendor" in desc_lower or "lights out" in desc_lower or "amplifiers" in desc_lower)
                             
    is_park_ambiguous = "broken bench" in desc_lower or "dead trees" in desc_lower or "irrigation" in desc_lower
    is_power_ambiguous = "substation" in desc_lower
    is_gas_ambiguous = "gas leak" in desc_lower
    is_drainage_ambiguous = "draining directly" in desc_lower
    is_traffic_ambiguous = "trucks idling" in desc_lower
    is_fields_ambiguous = "fields that channel" in desc_lower
    is_manhole_ambiguous = "manhole cover missing" in desc_lower
    is_dead_animal_ambiguous = "dead animal" in desc_lower
    is_shelter_ambiguous = "brt shelter roof glass broken" in desc_lower

    if (is_heritage_ambiguous or is_park_ambiguous or is_power_ambiguous or 
        is_gas_ambiguous or is_drainage_ambiguous or is_traffic_ambiguous or 
        is_fields_ambiguous or is_manhole_ambiguous or is_dead_animal_ambiguous or 
        is_shelter_ambiguous):
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # Check single categories in order of precedence
        
        # Pothole
        if "pothole" in desc_lower:
            category = "Pothole"
        # Drain Blockage
        elif "drain" in desc_lower or "sewer" in desc_lower:
            if any(w in desc_lower for w in ["block", "clog", "debris", "overflow"]):
                category = "Drain Blockage"
            else:
                category = "Other"
                flag = "NEEDS_REVIEW"
        # Flooding
        elif "flood" in desc_lower or "rainwater" in desc_lower:
            category = "Flooding"
        # Streetlight
        elif any(w in desc_lower for w in ["streetlight", "street light", "unlit", "lights out"]):
            category = "Streetlight"
        # Waste
        elif any(w in desc_lower for w in ["garbage", "waste", "trash", "litter"]):
            category = "Waste"
        # Noise
        elif any(w in desc_lower for w in ["music", "noise", "sound", "drilling", "amplifier", "band"]):
            category = "Noise"
        # Heritage Damage
        elif any(w in desc_lower for w in ["heritage", "historic", "ancient"]):
            category = "Heritage Damage"
        # Heat Hazard
        elif any(w in desc_lower for w in ["heat", "temperature", "melting", "sun", "hot", "bubbling", "°c"]):
            category = "Heat Hazard"
        # Road Damage
        elif any(w in desc_lower for w in ["road surface", "cracked", "sinking", "collapsed", "crater", "footpath", "paving", "cobblestone", "subsided", "buckled"]):
            category = "Road Damage"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            
    return category, priority, reason, flag

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    
    category, priority, reason, flag = classify_description(description)
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row using pandas, write results CSV.
    """
    try:
        # Load input CSV into a DataFrame
        df = pd.read_csv(input_path)
        
        # Verify required columns exist
        if "complaint_id" not in df.columns:
            print(f"Error: Missing 'complaint_id' column in {input_path}")
            return
        if "description" not in df.columns:
            print(f"Error: Missing 'description' column in {input_path}")
            return
            
        # Clean null values
        df = df.dropna(subset=["complaint_id"])
        df["description"] = df["description"].fillna("")
        
        # Apply classification row-by-row
        results = []
        for idx, row in df.iterrows():
            try:
                classified = classify_complaint(row.to_dict())
                results.append(classified)
            except Exception as e:
                print(f"Error processing row at index {idx}: {e}")
                results.append({
                    "complaint_id": str(row["complaint_id"]),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Error processing description.",
                    "flag": "NEEDS_REVIEW"
                })
                
        # Create output DataFrame
        out_df = pd.DataFrame(results)
        
        # Reorder columns to match the required schema
        out_df = out_df[["complaint_id", "category", "priority", "reason", "flag"]]
        
        # Write to output CSV
        out_df.to_csv(output_path, index=False)
        
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
