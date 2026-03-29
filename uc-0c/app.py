import csv
import argparse
import sys

def load_dataset(filepath: str) -> list:
    """
    Reads CSV, validates columns, reports null count and identifies which rows 
    contain null actual_spend values with their notes before returning data.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Missing required columns. Expected: {required_columns}")
            
            data = list(reader)
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Cannot read file: {e}")

    # Report null count and which rows
    null_rows = [row for row in data if not row.get('actual_spend', '').strip()]
    print(f"Dataset loaded. Found {len(null_rows)} rows with null actual_spend:")
    for row in null_rows:
        print(f"  - {row['period']} · {row['ward']} · {row['category']} · Reason: {row['notes']}")

    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates specific growth metrics for a given ward and category over time, 
    and returns a per-period table showing the formula used.
    """
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified. I cannot guess the growth type. Please provide it explicitly.")

    # Filter data without unauthorized aggregation
    # Only keep rows exactly matching ward and category
    filtered = [row for row in data if row.get('ward') == ward and row.get('category') == category]
    
    # Sort by period to ensure sequential evaluation
    filtered.sort(key=lambda x: x.get('period', ''))

    results = []
    
    for i, current_row in enumerate(filtered):
        period = current_row.get('period', '')
        actual_spend_str = current_row.get('actual_spend', '').strip()
        notes = current_row.get('notes', '').strip()
        
        if not actual_spend_str:
            # actual_spend is null
            growth_str = f"FLAGGED: actual_spend is null. Reason -> {notes}"
            actual_spend_val = "NULL"
        else:
            current_val = float(actual_spend_str)
            actual_spend_val = str(current_val)
            
            # Find previous value based on growth_type
            if growth_type.upper() == "MOM":
                # Previous month is i-1 if it exists and is adjacent
                if i > 0:
                    prev_row = filtered[i-1]
                    prev_spend_str = prev_row.get('actual_spend', '').strip()
                    if prev_spend_str:
                        prev_val = float(prev_spend_str)
                        if prev_val == 0:
                            growth_str = "Cannot compute (previous is 0)"
                        else:
                            growth = ((current_val - prev_val) / prev_val) * 100
                            sign = "+" if growth > 0 else ""
                            notes_str = f" ({notes})" if notes else ""
                            growth_str = f"{sign}{growth:.1f}%{notes_str} [Formula: (({current_val} - {prev_val}) / {prev_val}) * 100]"
                    else:
                        growth_str = "Cannot compute (previous period is null)"
                else:
                    growth_str = "n/a (first period)"
            elif growth_type.upper() == "YOY":
                try:
                    year, month = map(int, period.split('-'))
                    prev_period = f"{year-1}-{month:02d}"
                    # find row with prev_period
                    prev_row = next((r for r in filtered if r.get('period') == prev_period), None)
                    if prev_row:
                        prev_spend_str = prev_row.get('actual_spend', '').strip()
                        if prev_spend_str:
                            prev_val = float(prev_spend_str)
                            if prev_val == 0:
                                growth_str = "Cannot compute (previous is 0)"
                            else:
                                growth = ((current_val - prev_val) / prev_val) * 100
                                sign = "+" if growth > 0 else ""
                                notes_str = f" ({notes})" if notes else ""
                                growth_str = f"{sign}{growth:.1f}%{notes_str} [Formula: (({current_val} - {prev_val}) / {prev_val}) * 100]"
                        else:
                            growth_str = "Cannot compute (previous period is null)"
                    else:
                        growth_str = "n/a (previous year not found)"
                except ValueError:
                    growth_str = "Invalid period format for YoY"
            else:
                raise ValueError(f"REFUSAL: Unknown growth-type '{growth_type}'. Only MoM and YoY are supported.")
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual_spend_val,
            f'{growth_type} Growth': growth_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    try:
        # Check rule 1: Refuse aggregation across wards or categories.
        # Both --ward and --category must be provided.
        if not args.ward or not args.category:
            raise ValueError("REFUSAL: I am forbidden from aggregating across wards or categories. You must specify both --ward and --category explicitly.")

        # Agent Skill 1: load_dataset
        data = load_dataset(args.input)
        
        # Agent Skill 2: compute_growth
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write out
        if not results:
            print(f"No data found for ward '{args.ward}' and category '{args.category}'.")
            sys.exit(0)
            
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Calculation complete. Table successfully written to {args.output}")
    except Exception as e:
        print(f"{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
