"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()
    complaint_id = row.get("complaint_id", "").strip()
    
    category = "Other"
    flag = ""
    trigger_words = []
    
    # 1. Category Classification logic based on keywords
    if "pothole" in desc_lower:
        category = "Pothole"
        trigger_words.append("pothole")
    elif "drain" in desc_lower or "drainage" in desc_lower:
        category = "Drain Blockage"
        trigger_words.append("drain")
        if "flood" in desc_lower or "rainwater" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif "flood" in desc_lower or "rainwater" in desc_lower or "floods" in desc_lower:
        category = "Flooding"
        trigger_words.append("flood")
    elif "streetlight" in desc_lower or "lights out" in desc_lower or "unlit" in desc_lower or "darkness" in desc_lower or "lamp post" in desc_lower:
        category = "Streetlight"
        trigger_words.append("streetlight")
        if "heritage" in desc_lower or "historic" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif "waste" in desc_lower or "garbage" in desc_lower or "bins" in desc_lower or "dumped" in desc_lower or "animal" in desc_lower:
        category = "Waste"
        trigger_words.append("waste")
        if "heritage" in desc_lower or "historic" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif "music" in desc_lower or "drilling" in desc_lower or "audible" in desc_lower or "amplifiers" in desc_lower or "idling" in desc_lower or "noise" in desc_lower:
        category = "Noise"
        trigger_words.append("noise/sound")
        if "heritage" in desc_lower or "historic" in desc_lower or "museum" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif "temperature" in desc_lower or "melting" in desc_lower or "heatwave" in desc_lower or "bubbling" in desc_lower or "sun" in desc_lower or "burns" in desc_lower or "44°c" in desc_lower or "45°c" in desc_lower or "52°c" in desc_lower:
        category = "Heat Hazard"
        trigger_words.append("heat/temperature")
        if "broken" in desc_lower or "divider" in desc_lower or "glass" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower or "museum" in desc_lower:
        category = "Heritage Damage"
        trigger_words.append("heritage/historic")
        if "road" in desc_lower or "cobblestones" in desc_lower or "street" in desc_lower or "building" in desc_lower:
            flag = "NEEDS_REVIEW"
    elif any(kw in desc_lower for kw in ["road", "paving", "bridge", "footpath", "surface", "tarmac", "manhole", "tiles", "sideways", "walkway"]):
        category = "Road Damage"
        trigger_words.append("road/infrastructure")
        if "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower:
            flag = "NEEDS_REVIEW"
            
    if category == "Other":
        flag = "NEEDS_REVIEW"
        trigger_words.append("other context")

    # 2. Priority classification logic based on safety keywords
    severity_keywords = ["injury", "injured", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # 3. Reason generation (one sentence citing specific words from description)
    # Find a good phrase to quote
    quoted_phrase = ""
    # simple sentence splitting or phrase extraction
    sentences = desc.split(".")
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        # check if this sentence has any of the category-triggering words or the category name
        s_lower = s_clean.lower()
        if any(w in s_lower for w in trigger_words) or category.lower() in s_lower:
            quoted_phrase = s_clean
            break
    if not quoted_phrase and sentences:
        quoted_phrase = sentences[0].strip()
        
    reason = f"Classified as {category} because the complaint description explicitly mentions '{quoted_phrase}'."
    
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
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    results = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not any(row.values()):
                continue
            classified = classify_complaint(row)
            results.append(classified)
            
    # Write to output file
    # Ensure directory exists
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

