import pandas as pd
import argparse
import os
import re

class ComplaintClassifier:
    def __init__(self):
        self.allowed_categories = [
            "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
            "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
        ]
        self.severity_keywords = [
            "injury", "child", "school", "hospital", "ambulance", 
            "fire", "hazard", "fell", "collapse"
        ]

    def classify_complaint(self, description):
        """
        Skill: classify_complaint
        Processes a single citizen complaint to determine its category, priority level, and justification.
        """
        desc_lower = str(description).lower()
        
        # 1. Category logic (Simulated NLP logic matching schema)
        # In a real app, this would use an LLM or keyword matcher
        category = "Other"
        if "pothole" in desc_lower: category = "Pothole"
        elif "flood" in desc_lower or "water logging" in desc_lower: category = "Flooding"
        elif "light" in desc_lower or "dark" in desc_lower: category = "Streetlight"
        elif "garbage" in desc_lower or "waste" in desc_lower: category = "Waste"
        elif "noise" in desc_lower or "loud" in desc_lower: category = "Noise"
        elif "drain" in desc_lower or "sewage" in desc_lower: category = "Drain Blockage"
        
        # Error Handling: Taxonomy drift / Hallucination check
        if category not in self.allowed_categories:
            category = "Other"

        # 2. Priority logic (Enforcement Rule: Severity Keywords)
        priority = "Standard"
        found_severity = [word for word in self.severity_keywords if word in desc_lower]
        if found_severity:
            priority = "Urgent"
        elif "low" in desc_lower:
            priority = "Low"

        # 3. Reason logic (Enforcement Rule: One sentence citing words)
        if found_severity:
            reason = f"High priority assigned because the description mentions {found_severity[0]}."
        else:
            reason = f"Classified as {category} based on the mention of key infrastructure terms."

        # 4. Flag logic (Ambiguity check)
        flag = ""
        if category == "Other" or len(desc_lower.split()) < 4:
            flag = "NEEDS_REVIEW"

        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    def batch_classify(self, input_path, output_path):
        """
        Skill: batch_classify
        Reads input CSV, applies classify_complaint per row, writes output CSV.
        """
        if not os.path.exists(input_path):
            print(f"Error: Input file {input_path} not found.")
            return

        try:
            df = pd.read_csv(input_path)
            
            results = []
            for _, row in df.iterrows():
                # Assuming the description column is the first one if not named
                desc = row['description'] if 'description' in df.columns else row.iloc[0]
                results.append(self.classify_complaint(desc))

            res_df = pd.DataFrame(results)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            res_df.to_csv(output_path, index=False)
            print(f"Success: Results written to {output_path}")

        except Exception as e:
            print(f"Error during batch processing: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    classifier = ComplaintClassifier()
    classifier.batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()