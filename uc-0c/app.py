"""
UC-0C app.py — Compute infrastructure spend growth.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, reports null count and exact rows.
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            if not all(col in reader.fieldnames for col in required_cols):
                raise ValueError("Missing required columns in dataset.")
                
            null_count = 0
            for row in reader:
                if not row['actual_spend'].strip():
                    null_count += 1
                    print(f"FLAG: Null actual_spend found for Period: {row['period']}, Ward: {row['ward']}, Category: {row['category']} - Reason: {row['notes']}")
                data.append(row)
                
            if null_count > 0:
                print(f"Total null rows flagged: {null_count}")
                
            return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    """
    Computes per-period growth. Refuses unrequested aggregation.
    """
    if not growth_type:
        print("ERROR: Growth type not specified. Please provide a growth type (e.g., MoM). I will not guess.")
        sys.exit(1)
        
    if not ward or ward.lower() in ["any", "all", ""]:
        print("ERROR: Explicit ward not provided. I will not aggregate across multiple wards.")
        sys.exit(1)
        
    if not category or category.lower() in ["any", "all", ""]:
        print("ERROR: Explicit category not provided. I will not aggregate across multiple categories.")
        sys.exit(1)
        
    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered_data:
        spend_str = row['actual_spend'].strip()
        
        if not spend_str:
            results.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'actual_spend': 'NULL',
                'growth': f"Flagged Null: {row['notes']}",
                'formula': 'N/A'
            })
            prev_spend = None  # Reset because we can't compute next month's MoM from a null
            continue
            
        current_spend = float(spend_str)
        
        if prev_spend is None:
            growth = "N/A"
            formula = "First valid period or after null"
        else:
            if growth_type.lower() == 'mom':
                if prev_spend == 0:
                    growth = "N/A"
                else:
                    g_val = ((current_spend - prev_spend) / prev_spend) * 100
                    growth = f"{'+' if g_val > 0 else ''}{g_val:.1f}%"
                formula = "(Current - Previous) / Previous * 100"
            else:
                 growth = "Unsupported growth type"
                 formula = "N/A"
                 
        results.append({
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': current_spend,
            'growth': growth,
            'formula': formula
        })
        
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=False, help="Target ward")
    parser.add_argument("--category", required=False, help="Target category")
    parser.add_argument("--growth-type", required=False, help="Growth type (MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    # Check if arguments were passed manually for specific errors
    if '--growth-type' not in sys.argv:
         print("ERROR: Growth type not specified. Please provide a growth type (e.g., MoM). I will not guess.")
         sys.exit(1)
         
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
         with open(args.output, 'w', newline='', encoding='utf-8') as f:
             writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula'])
             writer.writeheader()
             writer.writerows(results)
             print(f"Done. Growth calculated and saved to {args.output}")

if __name__ == "__main__":
    main()
