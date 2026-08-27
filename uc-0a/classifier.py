import argparse
import pandas as pd

def classify_complaint(description):
    description_lower = str(description).lower()
    
    categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
    ]
    
    category = "Other"
    flag = ""
    
    matched_cats = [cat for cat in categories if cat.lower() in description_lower]
    if len(matched_cats) == 1:
        category = matched_cats[0]
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in description_lower]
    
    if found_urgent:
        priority = "Urgent"
        reason = f"Priority escalated to Urgent due to severity keyword '{found_urgent[0]}'."
    else:
        priority = "Standard"
        reason = "Standard priority case without any identified severity criteria."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    print(f"Processing {len(df)} complaints...")

    results = []
    for index, row in df.iterrows():
        prediction = classify_complaint(row.get('description', ''))
        results.append(prediction)
    
    output_df = pd.DataFrame(results)
    final_output = pd.concat([df, output_df], axis=1)
    final_output.to_csv(output_path, index=False)
    print(f"Success! Saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)