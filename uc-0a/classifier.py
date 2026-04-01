import csv
import argparse
import sys

# Allowed Categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Priority Triggers
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row):
    """
    Applies classification logic based on RICE rules in agents.md.
    """
    description = row.get('description', '').lower()
    location = row.get('location', '').lower()
    complaint_id = row.get('complaint_id', '')
    
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    # 1. Categorization Logic
    if "pothole" in description or "pothole" in location:
        category = "Pothole"
    elif any(kw in description for kw in ["flood", "waterlogging", "rain water"]):
        category = "Flooding"
    elif any(kw in description for kw in ["streetlight", "unlit", "street light", "dark"]):
        category = "Streetlight"
    elif any(kw in description for kw in ["waste", "garbage", "trash", "overflowing", "bins", "clearance"]):
        category = "Waste"
    elif any(kw in description for kw in ["noise", "music", "loudspeaker", "audible"]):
        category = "Noise"
    elif any(kw in description for kw in ["tarmac", "melting", "road surface", "paving", "subsidence", "cracked", "road damage"]):
        category = "Road Damage"
    elif any(kw in description for kw in ["heritage", "ancient", "old city", "historic"]):
        category = "Heritage Damage"
    elif any(kw in description for kw in ["heat", "temperature", "melting", "sun", "hot", "burns"]):
        # Some overlap with Road Damage, but let's prioritize Heat Hazard if temperature is mentioned
        if "temperature" in description or "sun" in description or "heat" in description:
            category = "Heat Hazard"
    elif any(kw in description for kw in ["drain", "sewage", "blockage", "sewer"]):
        category = "Drain Blockage"

    # Refine categorization for specific Ahmedabad data
    if "tarmac surface melting" in description or "metal bus shelter" in description or "heatwave" in description:
        category = "Heat Hazard"
    if "heritage area" in description or "old city" in description or "step well" in description:
        category = "Heritage Damage"
    if "waste" in description or "bins" in description:
        category = "Waste"

    # 2. Priority Logic
    if any(kw in description for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    
    # 3. Reason Logic (One sentence citing words)
    if category == "Heat Hazard":
        reason = f"Classified as Heat Hazard because description mentions '{next((kw for kw in ['melting', 'temperature', 'heatwave', 'sun'] if kw in description), 'heat')}'."
    elif category == "Heritage Damage":
        reason = f"Classified as Heritage Damage because description mentions '{next((kw for kw in ['heritage', 'old city', 'step well'] if kw in description), 'historic')}'."
    elif category == "Waste":
        reason = f"Classified as Waste because description mentions '{next((kw for kw in ['waste', 'bins', 'overflowing'] if kw in description), 'garbage')}'."
    elif category == "Road Damage":
        reason = f"Classified as Road Damage because description mentions '{next((kw for kw in ['road surface', 'paving', 'subsidence'] if kw in description), 'road')}'."
    else:
        reason = f"Classified as {category} based on keywords in description."

    # 4. Flag Logic (Ambiguity)
    if "heritage" in description and ("subsidence" in description or "road" in description):
        flag = "NEEDS_REVIEW"  # Ambiguous between Road Damage and Heritage Damage
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path, output_path):
    """
    Processes the input CSV and writes classification results to the output CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                results.append(classify_complaint(row))
        
        if not results:
            print("No data found in input file.")
            return

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Successfully processed {len(results)} complaints.")
        print(f"Output saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify citizen complaints.")
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
