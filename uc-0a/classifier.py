import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    if desc is None:
        desc = ""
    desc = desc.strip()
    complaint_id = row.get("complaint_id", "")
    
    # 1. Error handling for empty or null description
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = desc.lower()
    
    # 2. Priority severity keywords check (case-insensitive)
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    
    # 3. Category matching logic based on keyword scoring
    scores = {
        "Pothole": 0,
        "Flooding": 0,
        "Streetlight": 0,
        "Waste": 0,
        "Noise": 0,
        "Road Damage": 0,
        "Heritage Damage": 0,
        "Heat Hazard": 0,
        "Drain Blockage": 0,
        "Other": 0
    }
    
    # Keyword matches
    if "pothole" in desc_lower:
        scores["Pothole"] += 5
    if "potholes" in desc_lower:
        scores["Pothole"] += 5
        
    if "flood" in desc_lower or "flooding" in desc_lower or "floods" in desc_lower or "waterlogging" in desc_lower:
        scores["Flooding"] += 3
    if "rain" in desc_lower or "rainwater" in desc_lower:
        scores["Flooding"] += 2
        
    if "streetlight" in desc_lower or "streetlights" in desc_lower or "street light" in desc_lower or "street lights" in desc_lower or "lamp post" in desc_lower or "lighting" in desc_lower:
        scores["Streetlight"] += 4
    if "unlit" in desc_lower or "lights out" in desc_lower or "sparking" in desc_lower or "flickering" in desc_lower:
        scores["Streetlight"] += 3
        
    if "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower or "trash" in desc_lower or "litter" in desc_lower or "dumped" in desc_lower or "debris" in desc_lower:
        scores["Waste"] += 4
    if "dead animal" in desc_lower or "carcass" in desc_lower:
        scores["Waste"] += 5
        
    if "noise" in desc_lower or "music" in desc_lower or "loud" in desc_lower or "speaker" in desc_lower or "drilling" in desc_lower or "sound" in desc_lower or "band" in desc_lower:
        scores["Noise"] += 4
        
    if "cracked" in desc_lower or "sinking" in desc_lower or "footpath" in desc_lower or "tiles" in desc_lower or "bridge" in desc_lower or "tarmac" in desc_lower or "paving" in desc_lower or "cobblestones" in desc_lower or "broken bench" in desc_lower or "pavement" in desc_lower:
        scores["Road Damage"] += 3
    if "road surface" in desc_lower or "road" in desc_lower:
        scores["Road Damage"] += 1
        
    if "heritage" in desc_lower or "historic" in desc_lower or "museum" in desc_lower or "statue" in desc_lower or "monument" in desc_lower:
        scores["Heritage Damage"] += 5
        
    if "heat" in desc_lower or "temperature" in desc_lower or "hot" in desc_lower or "sun" in desc_lower or "heatwave" in desc_lower or "dehydration" in desc_lower or "shade" in desc_lower or "melting" in desc_lower:
        scores["Heat Hazard"] += 4
        
    if "drain" in desc_lower or "drainage" in desc_lower or "blocked" in desc_lower or "clogged" in desc_lower or "sewer" in desc_lower or "sewage" in desc_lower or "manhole" in desc_lower:
        scores["Drain Blockage"] += 4
        
    # Choose category with highest positive score
    active_categories = {k: v for k, v in scores.items() if v > 0}
    if not active_categories:
        category = "Other"
    else:
        category = max(active_categories, key=active_categories.get)
        
    # Ambiguity flagging logic
    flag = ""
    overlapping_categories = [k for k, v in active_categories.items() if v >= 3]
    if len(overlapping_categories) > 1:
        flag = "NEEDS_REVIEW"
    elif "heritage" in desc_lower or "historic" in desc_lower:
        if "lamp" in desc_lower or "light" in desc_lower or "road" in desc_lower or "street" in desc_lower or "cobblestones" in desc_lower or "music" in desc_lower or "waste" in desc_lower or "garbage" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif "manhole" in desc_lower:
        flag = "NEEDS_REVIEW"
    elif "drain" in desc_lower and ("flood" in desc_lower or "water" in desc_lower or "rain" in desc_lower):
        flag = "NEEDS_REVIEW"
        
    if category == "Other" and desc:
        flag = "NEEDS_REVIEW"

    # Priority setting
    priority = "Urgent" if is_urgent else "Standard"

    # Reason generation: extract matching sentence and wrap it in single sentence reason
    sentences = []
    current_sentence = []
    for char in desc:
        current_sentence.append(char)
        if char in ['.', '!', '?']:
            sentences.append("".join(current_sentence).strip())
            current_sentence = []
    if current_sentence:
        sentences.append("".join(current_sentence).strip())
    sentences = [s for s in sentences if s]
    
    citation_sentence = ""
    term_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rain", "water"],
        "Streetlight": ["light", "lamp", "unlit", "dark"],
        "Waste": ["garbage", "waste", "bin", "trash", "litter", "animal"],
        "Noise": ["music", "noise", "loud", "sound", "band"],
        "Road Damage": ["road", "footpath", "tile", "bridge", "paving", "surface", "cobblestones"],
        "Heritage Damage": ["heritage", "historic", "museum", "monument"],
        "Heat Hazard": ["heat", "temperature", "sun", "hot", "shade"],
        "Drain Blockage": ["drain", "blocked", "clogged", "sewer", "manhole"]
    }
    
    search_terms = term_map.get(category, [])
    for sentence in sentences:
        if any(term in sentence.lower() for term in search_terms):
            citation_sentence = sentence
            break
            
    if not citation_sentence and sentences:
        citation_sentence = sentences[0]
        
    if citation_sentence.endswith(('.', '!', '?')):
        citation_text = citation_sentence[:-1]
    else:
        citation_text = citation_sentence
        
    reason = f"Classified as {category} due to the mention of \"{citation_text}\" in the description."

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
    import os
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    results = []
    
    with open(input_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Empty CSV file or missing headers")
            
        required_cols = ["complaint_id", "description"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Required column '{col}' is missing from the header")
                
        for row in reader:
            try:
                # Basic validation & null flagging
                complaint_id = row.get("complaint_id")
                desc = row.get("description")
                
                # If complaint_id is missing, skip row
                if not complaint_id:
                    continue
                    
                # If description is missing/null, classify_complaint handles it and flags NEEDS_REVIEW
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                # Ensure we don't crash on bad rows, produce output even if some rows fail
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    # Write output file
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
