"""
UC-0C app.py — Compute dataset growth without silent dropping over aggregations.
"""
import argparse
import os
import pandas as pd

def load_dataset(input_path: str) -> str:
    """Reads the dataset using pandas, preserving structure for LLM."""
    df = pd.read_csv(input_path)
    return df.to_string(index=False)

def get_system_prompt() -> str:
    """Loads rules from agents.md to form the system instructions."""
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are a helpful municipal budget data analyst."

def compute_growth(dataset_text: str, ward: str, category: str, growth_type: str, system_prompt: str) -> str:
    """
    Compute growth using an LLM.
    """
    # TODO: Integrate your specific AI tool / SDK here.
    print(f"\n[WARNING] LLM integration is not configured. Returning mock summary for {ward} / {category} / {growth_type}.\n")
    return f"MOCK CSV OUTPUT:\nWard,Category,Period,Actual Spend,Growth Formula,Notes\n{ward},{category},2024-01,10.0,start,\n{ward},{category},2024-02,NULL,n/a,Flagged as Null"

def main():
    parser = argparse.ArgumentParser(description="Process budget data with strict null and aggregation checks.")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=False, help="Filter by specific ward")
    parser.add_argument("--category", required=False, help="Filter by specific category")
    parser.add_argument("--growth-type", required=False, help="Explicitly specify formula type (e.g. MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV table")
    
    args = parser.parse_args()
    
    print(f"Reading dataset from {args.input}...")
    dataset_text = load_dataset(args.input)
    
    system_prompt = get_system_prompt()
    
    print("Computing metrics...")
    output_table = compute_growth(
        dataset_text, 
        args.ward, 
        args.category, 
        args.growth_type, 
        system_prompt
    )
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_table)
        
    print(f"Success! Mock results saved to {args.output}")

if __name__ == "__main__":
    main()
