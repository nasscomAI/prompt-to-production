"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from typing import List, Dict

def load_dataset(input_path: str) -> List[Dict]:
    """
    Load and validate the ward budget CSV dataset.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        # Validate columns
        required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        if not all(col in data[0] for col in required_cols):
            raise ValueError(f"Missing required columns. Expected: {required_cols}")
        
        # Report nulls
        null_rows = [row for row in data if not row['actual_spend'].strip()]
        print(f"Loaded {len(data)} rows. Found {len(null_rows)} null actual_spend values.")
        for row in null_rows:
            print(f"  NULL: {row['period']} {row['ward']} {row['category']} - {row['notes']}")
        
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found")
    except Exception as e:
        raise Exception(f"Error loading dataset: {e}")

def compute_growth(data: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """
    Compute growth rates for specified ward and category.
    """
    if growth_type != 'MoM':
        raise ValueError("Only 'MoM' growth type is supported. Please specify --growth-type MoM")
    
    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered:
        print(f"No data found for ward '{ward}' and category '{category}'")
        return []
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    previous_spend = None
    
    for row in filtered:
        period = row['period']
        actual_spend = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        if not actual_spend:
            # Null value
            growth_rate = f"NULL - {notes}" if notes else "NULL"
            formula = "Not computed due to null actual_spend"
        else:
            try:
                current_spend = float(actual_spend)
                if previous_spend is None:
                    # First period
                    growth_rate = "N/A (first period)"
                    formula = "No previous period to compare"
                else:
                    if previous_spend == 0:
                        growth_rate = "Infinity (division by zero)"
                        formula = "((current - previous) / previous) * 100 but previous = 0"
                    else:
                        growth = ((current_spend - previous_spend) / previous_spend) * 100
                        growth_rate = ".1f"
                        formula = ".1f"
                previous_spend = current_spend
            except ValueError:
                growth_rate = "ERROR - invalid number"
                formula = "Could not parse actual_spend as float"
        
        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual_spend if actual_spend else 'NULL',
            'growth_rate': growth_rate,
            'formula': formula,
            'notes': notes
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, choices=['MoM'], help="Growth type (only MoM supported)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if results:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth_rate', 'formula', 'notes'])
                writer.writeheader()
                writer.writerows(results)
            print(f"Growth calculation complete. Results written to {args.output}")
        else:
            print("No results to write.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
