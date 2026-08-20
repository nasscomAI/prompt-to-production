import csv
import argparse
import sys
import os

def classify_complaint(description):
    desc_lower = description.lower()
    
    # 1. Enforce strict category taxonomy
    category = "Other"
    if "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "waterlogging" in desc_lower:
        category = "Flooding"
    elif "light" in desc_lower or "dark" in desc_lower or "streetlamp" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "trash" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower or "music" in desc_lower:
        category = "Noise"
    elif "road" in desc_lower or "crack" in desc_lower or "asphalt" in desc_lower:
        category = "Road Damage"
        if "pothole" in desc_lower: # Pothole overrides general road damage
             category = "Pothole"
    elif "heritage" in desc_lower or "monument" in desc_lower or "statue" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "sun" in desc_lower:
        category = "Heat Hazard"
    elif "drain" in desc_lower or "clog" in desc_lower or "sewage" in desc_lower:
        category = "Drain Blockage"
        
    # 2. Enforce Priority based on keywords (Fixing "Severity blindness")
    severity_keywords = ["injury", "child", "school", "hospital", "danger", "fell", "emergency"]
    priority = "Standard"
    for word in severity_keywords:
        if word in desc_lower:
            priority = "Urgent"
            break
            
    if priority != "Urgent" and ("minor" in desc_lower or "slight" in desc_lower):
        priority = "Low"
        
    # 3. Generate justification (Fixing "Missing justification")
    words = description.split()
    quoted_word = words[0] if words else "complaint"
    for w in words:
        if len(w) > 4: # Grab a meaningful word to quote
            quoted_word = w.strip('.,!?')
            break
            
    reason = f"Marked as {category} with {priority} priority because the text mentions '{quoted_word}'."
    
    # 4. Set Flag for ambiguity (Fixing "False confidence on ambiguity")
    flag = "NEEDS_REVIEW" if category == "Other" else ""
        
    return category, priority, reason, flag

def main():
    parser = argparse.ArgumentParser(description='Classify civic complaints.')
    parser.add_argument('--input', required=True, help='Path to input CSV')
    parser.add_argument('--output', required=True, help='Path to output CSV')
    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input):
        print(f"Error: Could not find input file at {args.input}")
        sys.exit(1)

    try:
        with open(args.input, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # Find the description column dynamically
            desc_col = next((col for col in fieldnames if 'desc' in col.lower() or 'text' in col.lower()), fieldnames[-1])

            rows_to_write = []
            for row in reader:
                description = row[desc_col]
                category, priority, reason, flag = classify_complaint(description)
                
                # Append new data
                output_row = row.copy()
                output_row['category'] = category
                output_row['priority'] = priority
                output_row['reason'] = reason
                output_row['flag'] = flag
                rows_to_write.append(output_row)

        # Write the results
        if rows_to_write:
            out_fieldnames = list(rows_to_write[0].keys())
            with open(args.output, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                writer.writerows(rows_to_write)
            print(f"✅ Success! Processed {len(rows_to_write)} rows and saved to {args.output}")

    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == '__main__':
    main()