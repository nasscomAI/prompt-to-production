import argparse
import csv

def load_dataset(filepath: str):
    """Load the dataset and validate rows according to requested constraints."""
    data_rows = []
    
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            # Parse numerics
            try:
                if row['actual_spend'].strip() == '':
                    row['actual_spend'] = None
                else:
                    row['actual_spend'] = float(row['actual_spend'])
                    
                row['budgeted_amount'] = float(row['budgeted_amount'])
            except ValueError:
                pass # Rely on validation rules instead of crashing
                
            data_rows.append(row)
            
    return data_rows

def compute_growth(dataset: list, target_ward: str, target_category: str, growth_type: str):
    """Compute period-over-period growth for a specific ward and category."""
    
    # 1. Enforcement rule: Never aggregate across wards/categories
    if not target_ward or target_ward.lower() == "all" or not target_category or target_category.lower() == "all":
        raise ValueError("REFUSED: Aggregation across multiple wards or categories is strictly prohibited by policy.")
        
    # 4. Enforcement rule: Explicit growth type required
    if growth_type != "MoM":
        # YoY or others are not implemented in the basic script.
        raise ValueError(f"REFUSED: Unrecognized or missing explicit growth-type '{growth_type}'. Only 'MoM' is supported.")
        
    # Filter dataset
    filtered = [row for row in dataset if row['ward'] == target_ward and row['category'] == target_category]
    
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    output_rows = []
    previous_spend = None
    
    for row in filtered:
        current_spend = row['actual_spend']
        period = row['period']
        notes = row.get('notes', '')
        
        out_row = {
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": current_spend if current_spend is not None else "NULL",
            "growth_type": growth_type,
            "growth_pct": "n/a",
            "formula": "n/a",
            "flag": ""
        }
        
        # 2. Enforcement rule: Explicitly flag NULL values
        if current_spend is None:
            out_row["growth_pct"] = "NULL"
            out_row["formula"] = "Cannot compute: current period is NULL"
            out_row["flag"] = f"[FLAG] NULL value: {notes}"
        elif previous_spend is None and len(output_rows) > 0:
            out_row["growth_pct"] = "NULL"
            out_row["formula"] = "Cannot compute: previous period is NULL"
            out_row["flag"] = "[FLAG] Previous period value was NULL"
        elif previous_spend is not None:
            # Calculate MoM
            growth = ((current_spend - previous_spend) / previous_spend) * 100
            out_row["growth_pct"] = f"{growth:+.1f}%"
            # 3. Enforcement rule: Explicit formula display
            out_row["formula"] = f"({current_spend} - {previous_spend}) / {previous_spend} * 100"
            out_row["flag"] = ""
        else:
            out_row["formula"] = "First period: no previous data"
            
        output_rows.append(out_row)
        previous_spend = current_spend
        
    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=True, help="Type of growth to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output resulting CSV")
    
    args = parser.parse_args()
    
    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"Warning: No data found for Ward: '{args.ward}' and Category: '{args.category}'")
            return
            
        # Write to output CSV
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth_type", "growth_pct", "formula", "flag"])
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Done. Results written to {args.output}")
        
    except Exception as e:
        print(f"Error executing request: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
