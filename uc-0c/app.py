"""
UC-0C app.py — Budget Growth Analysis CLI
Following the RICE framework and enforcement rules in agents.md.
"""
import argparse
import sys
from classifier import process_analysis

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth results")
    
    args = parser.parse_args()

    # Enforcement Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type must be specified. Please use 'MoM'.")
        sys.exit(1)

    print(f"Analyzing growth for Ward: {args.ward}, Category: {args.category}")
    print(f"Growth Type: {args.growth_type}")
    
    try:
        count = process_analysis(
            args.input, 
            args.output, 
            args.ward, 
            args.category, 
            args.growth_type
        )
        print(f"Success. Generated {count} periods of data.")
        print(f"Results written to: {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
