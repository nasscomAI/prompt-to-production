import pandas as pd
import argparse
import sys
import os

class BudgetAnalyzer:
    def __init__(self):
        self.required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']

    def load_dataset(self, file_path):
        """
        Skill: load_dataset
        Reads CSV, validates columns, reports null count and identifies rows.
        """
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            sys.exit(1)
            
        df = pd.read_csv(file_path)
        
        # Validate columns
        if not all(col in df.columns for col in self.required_columns):
            print(f"Error: Missing mandatory columns. Expected: {self.required_columns}")
            sys.exit(1)
            
        # Identify nulls (Enforcement Rule 2)
        null_mask = df['actual_spend'].isna()
        null_rows = df[null_mask]
        
        if not null_rows.empty:
            print(f"--- NULL VALUE AUDIT ---")
            for _, row in null_rows.iterrows():
                print(f"FLAGGED: {row['period']} | {row['ward']} | {row['category']}")
                print(f"REASON: {row['notes']}\n")
        
        return df

    def compute_growth(self, df, ward, category, growth_type):
        """
        Skill: compute_growth
        Returns per-period table with explicit formula strings.
        """
        # Enforcement Rule 1: Refuse aggregation
        # Filtering for specific ward and category is mandatory
        filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
        
        if filtered_df.empty:
            print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
            sys.exit(1)

        # Sort by period to ensure growth calculation is chronological
        filtered_df = filtered_df.sort_values('period')
        
        results = []
        
        for i in range(len(filtered_df)):
            current_row = filtered_df.iloc[i]
            current_val = current_row['actual_spend']
            
            res_row = {
                "Ward": current_row['ward'],
                "Category": current_row['category'],
                "Period": current_row['period'],
                "Actual Spend (₹ lakh)": current_val if pd.notna(current_val) else "NULL",
                "Growth Result": "n/a",
                "Formula": "n/a"
            }

            # Handle Nulls (Enforcement Rule 2)
            if pd.isna(current_val):
                res_row["Growth Result"] = "NULL - NOT COMPUTED"
                res_row["Formula"] = f"Calculation blocked: {current_row['notes']}"
            
            # Compute MoM (Enforcement Rule 3 & 4)
            elif i > 0:
                prev_val = filtered_df.iloc[i-1]['actual_spend']
                
                if pd.notna(prev_val) and prev_val != 0:
                    growth = ((current_val - prev_val) / prev_val) * 100
                    res_row["Growth Result"] = f"{growth:+.1f}%"
                    # Enforcement Rule 3: Show formula
                    res_row["Formula"] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
                else:
                    res_row["Growth Result"] = "Incalculable"
                    res_row["Formula"] = "Previous period value is NULL or Zero"
            
            results.append(res_row)

        return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analyzer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False) # We check this manually for Enforcement Rule 4
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    # Enforcement Rule 4: Refuse if growth-type is missing
    if not args.growth_type:
        print("CRITICAL ERROR: --growth-type not specified.")
        print("Please specify 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year).")
        sys.exit(1)

    analyzer = BudgetAnalyzer()
    
    # Skill 1: Load and Validate
    raw_data = analyzer.load_dataset(args.input)
    
    # Skill 2: Compute
    output_df = analyzer.compute_growth(
        raw_data, 
        args.ward, 
        args.category, 
        args.growth_type
    )

    # Save output
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    output_df.to_csv(args.output, index=False)
    print(f"Success: Growth report generated at {args.output}")

if __name__ == "__main__":
    main()