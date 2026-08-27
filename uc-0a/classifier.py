import pandas as pd
import argparse
import os

def batch_classify(input_path, output_path):
    # 1. Load the data
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    df = pd.read_csv(input_path)
    
    # 2. Apply classification logic (This reflects your agents.md rules)
    results = []
    for _, row in df.iterrows():
        desc = str(row['description']).lower()
        
        # Priority Logic based on keywords
        if any(word in desc for word in ['injury', 'hospital', 'school', 'child', 'electric']):
            priority = "Urgent"
            reasoning = "Safety risk: high-vulnerability location or injury mentioned."
        elif any(word in desc for word in ['dark', 'block', 'flood']):
            priority = "High"
            reasoning = "Major utility failure or access blockage."
        else:
            priority = "Medium"
            reasoning = "Standard maintenance request."

        # Category Logic
        if "hole" in desc: category = "Pothole"
        elif "light" in desc: category = "Streetlight"
        elif "water" in desc or "leak" in desc: category = "Water Leakage"
        elif "waste" in desc or "garbage" in desc: category = "Garbage"
        else: category = "Other"

        results.append({
            "category": category,
            "priority": priority,
            "reasoning": reasoning,
            "needs_review": False if category != "Other" else True
        })

    # 3. Merge and Save
    results_df = pd.DataFrame(results)
    final_df = pd.concat([df, results_df], axis=1)
    final_df.to_csv(output_path, index=False)
    print(f"✅ Success! Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)