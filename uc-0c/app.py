"""
UC-0C app.py — Budget Growth Analysis
"""

import argparse
import csv
import os
import sys

class ValidationError(ValueError):
    """Raised when data validation fails or business rules are violated."""
    pass

def validate_non_aggregation(ward: str, category: str):
    """
    Validates that the query is specific to a single ward and category.
    Rejects any inputs that suggest aggregation or multi-entity calculation.
    """
    refuse_keywords = {"all", "total", "average", "any", "aggregate", "summary", "mean", "sum", "combined"}
    
    # Check ward
    w_clean = ward.strip().lower()
    if not w_clean:
        raise ValidationError("Ward parameter is empty. Refusing request.")
    if "," in w_clean or w_clean in refuse_keywords:
        raise ValidationError(
            f"Refusing request: attempt to aggregate across multiple wards ('{ward}'). "
            "Please specify a single, specific ward (e.g., 'Ward 1 – Kasba')."
        )
        
    # Check category
    c_clean = category.strip().lower()
    if not c_clean:
        raise ValidationError("Category parameter is empty. Refusing request.")
    if "," in c_clean or c_clean in refuse_keywords:
        raise ValidationError(
            f"Refusing request: attempt to aggregate across multiple categories ('{category}'). "
            "Please specify a single, specific category (e.g., 'Roads & Pothole Repair')."
        )

def load_dataset(file_path: str) -> list:
    """
    Skill: load_dataset
    Reads the budget CSV dataset, validates columns, and reports the count
    and specific details of null actual_spend rows before returning the data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: Dataset not found at '{file_path}'")
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    records = []
    null_rows = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames:
                raise ValidationError("Dataset is empty or cannot be parsed as CSV.")
                
            # Clean and match headers
            fieldnames = [col.strip() for col in reader.fieldnames]
            if not required_cols.issubset(fieldnames):
                missing = required_cols - set(fieldnames)
                raise ValidationError(f"Key columns missing or misaligned in the dataset: {', '.join(missing)}")
                
            for idx, row in enumerate(reader, start=2):
                row_clean = {k.strip(): v for k, v in row.items()}
                
                # Check actual_spend
                spend_val = row_clean.get('actual_spend', '')
                if spend_val is None or spend_val.strip() == '' or spend_val.strip().lower() == 'null':
                    notes = row_clean.get('notes', '').strip()
                    null_rows.append({
                        'line': idx,
                        'period': row_clean.get('period', '').strip(),
                        'ward': row_clean.get('ward', '').strip(),
                        'category': row_clean.get('category', '').strip(),
                        'notes': notes if notes else "No note provided"
                    })
                    row_clean['actual_spend'] = None
                else:
                    try:
                        row_clean['actual_spend'] = float(spend_val.strip())
                    except ValueError:
                        raise ValidationError(
                            f"Column 'actual_spend' misalignment: invalid non-numeric value '{spend_val}' at row {idx}"
                        )
                
                # Check budgeted_amount
                budget_val = row_clean.get('budgeted_amount', '')
                if budget_val is None or budget_val.strip() == '':
                    row_clean['budgeted_amount'] = 0.0
                else:
                    try:
                        row_clean['budgeted_amount'] = float(budget_val.strip())
                    except ValueError:
                        raise ValidationError(
                            f"Column 'budgeted_amount' misalignment: invalid non-numeric value '{budget_val}' at row {idx}"
                        )
                        
                records.append(row_clean)
                
    except csv.Error as ce:
        raise ValidationError(f"CSV parsing error: {ce}")
        
    # Report null details before returning data (Enforcement Rule 2)
    print("----------------------------------------------------------------------")
    print(f"Validation Summary: Found {len(null_rows)} null actual_spend row(s)")
    for n in null_rows:
        print(f" - Line {n['line']}: Period: {n['period']} | Ward: {n['ward']} | Category: {n['category']} | Reason: {n['notes']}")
    print("----------------------------------------------------------------------")
    
    return records

def compute_growth(params: dict) -> list:
    """
    Skill: compute_growth
    Calculates growth for a specified ward and category based on the growth type,
    returning a per-period table that includes the formula used for each result.
    """
    dataset = params.get('dataset')
    ward = params.get('ward')
    category = params.get('category')
    growth_type = params.get('growth_type')
    
    # 1. Enforce that growth_type is specified (Enforcement Rule 4)
    if not growth_type:
        raise ValidationError(
            "Growth type (--growth-type) is not specified. Refusing execution. "
            "Please explicitly specify a growth type (e.g. 'MoM' or 'YoY')."
        )
        
    growth_type_upper = growth_type.strip().upper()
    if growth_type_upper not in ('MOM', 'YOY'):
        raise ValidationError(
            f"Ambiguous or unsupported growth type: '{growth_type}'. "
            "Please choose 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)."
        )
        
    # 2. Enforce non-aggregation rule (Enforcement Rule 1)
    validate_non_aggregation(ward, category)
    
    # Filter for the target ward and category
    filtered = [
        r for r in dataset 
        if r['ward'].strip() == ward.strip() and r['category'].strip() == category.strip()
    ]
    
    if not filtered:
        raise ValidationError(
            f"No data records found matching Ward: '{ward}' and Category: '{category}'. "
            "Please check the spelling and characters (e.g. en-dash '–')."
        )
        
    # Sort chronological
    filtered.sort(key=lambda x: x['period'])
    
    # Create lookup map for periods
    period_map = {r['period']: r for r in filtered}
    
    results = []
    for record in filtered:
        period = record['period']
        actual_spend = record['actual_spend']
        notes = record['notes'].strip() if record['notes'] else ''
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': 'NULL' if actual_spend is None else str(actual_spend),
            'growth': 'NULL',
            'formula': ''
        }
        
        # 3. Refuse calculation if target actual spend is null (Enforcement Rule 2)
        if actual_spend is None:
            reason = notes if notes else "No note provided"
            result_row['growth'] = 'NULL'
            result_row['formula'] = f"Refused: actual spend is NULL due to: {reason}"
            results.append(result_row)
            continue
            
        # Determine baseline period
        if growth_type_upper == 'MOM':
            try:
                year, month = map(int, period.split('-'))
                if month == 1:
                    prev_year = year - 1
                    prev_month = 12
                else:
                    prev_year = year
                    prev_month = month - 1
                baseline_period = f"{prev_year}-{prev_month:02d}"
            except Exception:
                baseline_period = None
        else: # YOY
            try:
                year, month = map(int, period.split('-'))
                baseline_period = f"{year-1}-{month:02d}"
            except Exception:
                baseline_period = None
                
        # Validate baseline
        if not baseline_period or baseline_period not in period_map:
            result_row['growth'] = 'NULL'
            result_row['formula'] = f"Refused: baseline period ({baseline_period if baseline_period else 'N/A'}) data missing"
        else:
            baseline_rec = period_map[baseline_period]
            baseline_spend = baseline_rec['actual_spend']
            
            if baseline_spend is None:
                baseline_reason = baseline_rec['notes'].strip() if baseline_rec['notes'] else "No note provided"
                result_row['growth'] = 'NULL'
                result_row['formula'] = f"Refused: baseline actual spend is NULL due to: {baseline_reason}"
            elif baseline_spend == 0.0:
                result_row['growth'] = 'NULL'
                result_row['formula'] = "Refused: baseline spend is 0.0 (division by zero)"
            else:
                # Compute growth
                diff = actual_spend - baseline_spend
                growth_rate = (diff / baseline_spend) * 100.0
                
                # Show formula used alongside the result (Enforcement Rule 3)
                formula_str = f"({actual_spend} - {baseline_spend}) / {baseline_spend}"
                
                if growth_rate > 0:
                    growth_str = f"+{growth_rate:.1f}%"
                elif growth_rate < 0:
                    growth_str = f"-{abs(growth_rate):.1f}%"
                else:
                    growth_str = "0.0%"
                    
                result_row['growth'] = growth_str
                result_row['formula'] = formula_str
                
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Ward and Category Budget Growth Analysis (UC-0C)")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    # Make --growth-type optional so we can check and refuse/ask explicitly
    parser.add_argument("--growth-type", required=False, default=None, help="Growth type calculation (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to save growth output CSV file")
    
    # Parse CLI args
    args = parser.parse_args()
    
    # Enforcement Rule 4: If growth_type not specified, refuse and ask
    if not args.growth_type or args.growth_type.strip() == "":
        print("ERROR: Growth type (--growth-type) was not specified.", file=sys.stderr)
        print("Please choose a valid growth type: '--growth-type MoM' or '--growth-type YoY'.", file=sys.stderr)
        sys.exit(1)
        
    try:
        # Load dataset and print validation details
        dataset = load_dataset(args.input)
        
        # Calculate growth based on target parameters
        params = {
            'dataset': dataset,
            'ward': args.ward,
            'category': args.category,
            'growth_type': args.growth_type
        }
        results = compute_growth(params)
        
        # Ensure target output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        # Write output CSV
        headers = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula']
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
                
        print(f"\nSUCCESS: Growth analysis written to '{args.output}'.")
        
    except (FileNotFoundError, ValidationError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
