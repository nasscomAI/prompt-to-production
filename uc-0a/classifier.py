import csv
import argparse
import os

def classify_complaint(description):
    """
    Classifies a single complaint based on keywords and rules.
    """
    desc_low = description.lower()
    
    # Categories and Keywords
    categories = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlogging", "inundation", "water log"],
        "Streetlight": ["light", "dark", "lamp", "blackout"],
        "Waste": ["garbage", "trash", "waste", "dump", "smell", "stink"],
        "Noise": ["noise", "loud", "music", "speaker", "sound"],
        "Road Damage": ["road", "crack", "surface", "asphalt"],
        "Heritage Damage": ["monument", "statue", "heritage", "ancient", "old building"],
        "Heat Hazard": ["heat", "sun", "hot", "dehydration"],
        "Drain Blockage": ["drain", "sewage", "gutter", "clog"],
    }
    
    # Priority Keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Determine Category
    category = "Other"
    for cat, keywords in categories.items():
        if any(kw in desc_low for kw in keywords):
            category = cat
            break
            
    # Determine Priority
    priority = "Standard"
    triggered_word = None
    for kw in urgent_keywords:
        if kw in desc_low:
            priority = "Urgent"
            triggered_word = kw
            break
            
    if priority != "Urgent":
        # Additional logic for Low priority could go here
        if len(desc_low) < 20:
            priority = "Low"

    # Reason and Flag
    if triggered_word:
        reason = f"Marked Urgent due to safety-related keyword: '{triggered_word}'."
    elif category != "Other":
        reason = f"Classified as {category} based on description keywords."
    else:
        reason = "Classified as Other due to lack of specific matches."
        
    flag = ""
    if category == "Other" or "help" in desc_low and "?" in desc_low:
        flag = "NEEDS_REVIEW"
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        
        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                classification = classify_complaint(row.get('description', ''))
                row.update(classification)
                writer.writerow(row)
                
    print(f"Successfully processed complaints. Output saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Civic Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
