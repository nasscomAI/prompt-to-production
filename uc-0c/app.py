"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates the target columns, and 
    explicitly reports the presence and reasons for any null values.
    """
    dataset = []
    null_report = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Basic schema validation
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing required columns. Expected: {required_cols}")

            for row in reader:
                # Store the row
                dataset.append(row)
                
                # Check for explicit nulls in our actual_spend column
                spend = row.get("actual_spend", "").strip()
                if not spend or spend.lower() == 'null':
                    null_report.append({
                        "period": row.get("period"),
                        "ward": row.get("ward"),
                        "category": row.get("category"),
                        "notes": row.get("notes")
                    })
                    
        return dataset, null_report
        
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        return None, None
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None, None

def compute_growth(dataset, target_ward, target_category, growth_type):
    """
    Computes the specified growth metric, attaching the formula used.
    Skips computation for null rows, preserving source notes.
    Refuses unauthorized aggregation over wards/categories.
    """
    if not target_ward or target_ward == "Any":
        return {"error": "REFUSED: Unauthorized aggregation. Must specify a complete ward."}
    if not target_category or target_category == "Any":
        return {"error": "REFUSED: Unauthorized aggregation. Must specify a complete category."}
    if not growth_type:
        return {"error": "REFUSED: Growth type (e.g., MoM, YoY) must be explicitly provided."}
        
    # Filter dataset strictly to the requested dimension
    filtered_data = [row for row in dataset if row['ward'] == target_ward and row['category'] == target_category]
    
    # Sort chronologically by period
    filtered_data = sorted(filtered_data, key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        spend_str = row['actual_spend'].strip()
        
        result_row = {
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": spend_str,
            "computed_growth": "",
            "formula_used": "",
            "notes": row['notes']
        }
        
        # Explicit Null Handling
        if not spend_str or spend_str.lower() == 'null':
            result_row['computed_growth'] = "FLAGGED"
            result_row['formula_used'] = "REFUSED: Null Data"
            # Notes from source are preserved automatically via the assignment above
            results.append(result_row)
            continue
            
        current_val = float(spend_str)
        
        # Calculate metric based on type
        if growth_type.upper() == "MOM":
            if i == 0:
                result_row['computed_growth'] = "n/a"
                result_row['formula_used'] = "Baseline period"
            else:
                prev_spend_str = filtered_data[i-1]['actual_spend'].strip()
                if not prev_spend_str or prev_spend_str.lower() == 'null':
                    result_row['computed_growth'] = "n/a"
                    result_row['formula_used'] = "REFUSED: Previous period is null"
                else:
                    prev_val = float(prev_spend_str)
                    if prev_val == 0:
                        result_row['computed_growth'] = "n/a"
                        result_row['formula_used'] = "Div by zero"
                    else:
                        growth = ((current_val - prev_val) / prev_val) * 100
                        result_row['computed_growth'] = f"{growth:+.1f}%"
                        result_row['formula_used'] = "(Actual - Prev) / Prev"
                        
        elif growth_type.upper() == "YOY":
            # Just a placeholder for YoY logic (assuming dataset doesn't have YoY for this 1 year exercise)
            result_row['computed_growth'] = "n/a"
            result_row['formula_used'] = "Requires 12+ months history"
        else:
            return {"error": f"REFUSED: Unknown growth type '{growth_type}'"}
            
        results.append(result_row)
        
    return {"data": results}

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to filter")
    parser.add_argument("--category", required=False, help="Specific category to filter")
    parser.add_argument("--growth-type", required=False, help="Formula to use (MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # 1. Load & Validate
    dataset, null_report = load_dataset(args.input)
    if not dataset:
        return
        
    # Agent Null Disclosure
    if null_report:
        print(f"Data Validation Warning: Found {len(null_report)} explicit null actual_spend rows.")
        for nr in null_report[:3]: # show first 3
            print(f" - {nr['period']} | {nr['ward']} | {nr['category']} -> {nr['notes']}")
        print("These rows will be flagged and bypassed for formula operations.\n")
        
    # 2. Compute
    computation_result = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Handle explicit refusals from the agent logic
    if "error" in computation_result:
        print(f"Computation Halted: {computation_result['error']}")
        return
        
    out_data = computation_result["data"]
    
    if not out_data:
        print("Warning: No data matched the given filters.")
        return
        
    # 3. Output
    try:
        keys = out_data[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(out_data)
            
        print(f"Done. Detailed line-item output written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
