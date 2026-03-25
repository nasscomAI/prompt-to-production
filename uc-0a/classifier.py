import csv
import argparse
import os

def classify_complaint(description):
    desc_lower = description.lower()
    
    # Category detection
    category = "Other"
    reason_keywords = []
    
    if "pothole" in desc_lower:
        category = "Pothole"
        reason_keywords.append("pothole")
    elif "flood" in desc_lower or "water" in desc_lower:
        if "drain" in desc_lower or "blockage" in desc_lower:
            category = "Drain Blockage"
            reason_keywords.append("drain/blockage")
        else:
            category = "Flooding"
            reason_keywords.append("flooded/water")
    elif "light" in desc_lower or "lamp" in desc_lower:
        if "heritage" in desc_lower:
            category = "Heritage Damage"
            reason_keywords.append("heritage/lights")
        else:
            category = "Streetlight"
            reason_keywords.append("lights")
    elif "waste" in desc_lower or "garbage" in desc_lower or "animal" in desc_lower:
        category = "Waste"
        reason_keywords.append("waste/garbage/animal")
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
        reason_keywords.append("noise/music")
    elif "road" in desc_lower or "surface" in desc_lower or "manhole" in desc_lower or "tile" in desc_lower:
        if "heritage" in desc_lower:
            category = "Heritage Damage"
            reason_keywords.append("heritage/road")
        else:
            category = "Road Damage"
            reason_keywords.append("road/surface/manhole")
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        reason_keywords.append("heritage")
    elif "heat" in desc_lower or "temperature" in desc_lower:
        category = "Heat Hazard"
        reason_keywords.append("heat")

    # Priority detection
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = False
    found_severity = []
    for sk in severity_keywords:
        if sk in desc_lower:
            is_urgent = True
            found_severity.append(sk)
    
    priority = "Urgent" if is_urgent else "Standard"
    
    # Reason: One sentence citing specific words
    reasons = [f"'{k}'" for k in reason_keywords]
    if found_severity:
        reasons.extend([f"'{s}'" for s in found_severity])
    
    reason = f"Classified as {category} because description mentions {', '.join(reasons)}."
    
    # Flag
    flag = ""
    if category == "Other" or "ambiguous" in desc_lower or "not sure" in desc_lower:
        flag = "NEEDS_REVIEW"
        
    return category, priority, reason, flag

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        return

    with open(args.input, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        
        results = []
        for row in reader:
            cat, prio, reas, flg = classify_complaint(row['description'])
            row['category'] = cat
            row['priority'] = prio
            row['reason'] = reas
            row['flag'] = flg
            results.append(row)
            
    with open(args.output, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Classification complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
