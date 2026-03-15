"""
UC-0C — Number That Looks Right
Calculates per-ward per-category budget totals and growth metrics without cross-aggregation.
"""
import argparse
import csv
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime


def filter_by_ward_and_category(rows: List[Dict[str, Any]], ward: str, category: str) -> List[Dict[str, Any]]:
    """
    Filter rows to match specified ward AND category.
    Returns only rows with exact match on both dimensions.
    """
    filtered = []
    for row in rows:
        row_ward = row.get('ward', '').strip()
        row_category = row.get('category', '').strip()
        
        if row_ward == ward and row_category == category:
            filtered.append(row)
    
    return filtered


def calculate_totals(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate totals for filtered rows.
    Returns dict with total_budgeted, total_actual_spend, null_count, variance.
    """
    total_budgeted = 0.0
    total_actual_spend = 0.0
    null_count = 0
    months_with_data = []
    
    for row in rows:
        try:
            budgeted = float(row.get('budgeted_amount', 0) or 0)
            actual = row.get('actual_spend', '')
            period = row.get('period', '')
            
            total_budgeted += budgeted
            
            if actual and actual.strip():
                try:
                    actual_val = float(actual)
                    total_actual_spend += actual_val
                    if period:
                        months_with_data.append(period)
                except ValueError:
                    null_count += 1
            else:
                null_count += 1
        except Exception as e:
            print(f"Warning: Error processing row: {e}")
            null_count += 1
    
    # Calculate variance
    if null_count == len(rows):
        variance = None
        variance_display = "Cannot calculate - all actual_spend values are null"
    else:
        variance = total_budgeted - total_actual_spend
        variance_display = f"{variance:.2f}"
    
    return {
        "total_budgeted": round(total_budgeted, 2),
        "total_actual_spend": round(total_actual_spend, 2) if null_count < len(rows) else None,
        "null_count": null_count,
        "variance": variance,
        "variance_display": variance_display,
        "months_with_data": sorted(set(months_with_data))
    }


def calculate_growth(rows: List[Dict[str, Any]], growth_type: str = "MoM") -> Dict[str, str]:
    """
    Calculate growth metrics (MoM or YoY) for actual_spend values.
    Returns dict mapping period to growth percentage or 'N/A'.
    """
    growth_map = {}
    
    # Sort rows by period
    sorted_rows = sorted(rows, key=lambda r: r.get('period', ''))
    
    # Build a map of period -> actual_spend
    period_map = {}
    for row in sorted_rows:
        period = row.get('period', '')
        actual = row.get('actual_spend', '')
        
        if period:
            if actual and actual.strip():
                try:
                    period_map[period] = float(actual)
                except ValueError:
                    period_map[period] = None
            else:
                period_map[period] = None
    
    # Calculate growth
    if growth_type == "MoM":
        periods = sorted(period_map.keys())
        for i in range(1, len(periods)):
            current_period = periods[i]
            prior_period = periods[i-1]
            
            current_val = period_map.get(current_period)
            prior_val = period_map.get(prior_period)
            
            if current_val is not None and prior_val is not None and prior_val != 0:
                growth = ((current_val - prior_val) / prior_val) * 100
                growth_map[current_period] = f"{growth:.1f}%"
            else:
                growth_map[current_period] = "N/A"
    
    return growth_map


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True, help="Ward name to calculate for")
    parser.add_argument("--category",    required=True, help="Category to calculate for")
    parser.add_argument("--growth-type", required=False, default="MoM", choices=["MoM", "YoY"], help="Growth calculation type")
    parser.add_argument("--output",      required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        # Read input CSV
        rows = []
        with open(args.input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print(f"Error: No data in {args.input}")
            sys.exit(1)
        
        print(f"Loaded {len(rows)} rows from {args.input}")
        
        # Filter by ward and category
        filtered_rows = filter_by_ward_and_category(rows, args.ward, args.category)
        
        if not filtered_rows:
            print(f"Warning: No data found for ward='{args.ward}', category='{args.category}'")
            print(f"Available wards: {set(r.get('ward', '') for r in rows)}")
            print(f"Available categories: {set(r.get('category', '') for r in rows)}")
        
        print(f"Filtered to {len(filtered_rows)} rows for ward='{args.ward}', category='{args.category}'")
        
        # Calculate totals
        totals = calculate_totals(filtered_rows)
        
        # Calculate growth
        growth = calculate_growth(filtered_rows, args.growth_type)
        
        # Prepare output rows
        output_rows = []
        
        for row in filtered_rows:
            output_row = {
                "period": row.get('period', ''),
                "ward": row.get('ward', ''),
                "category": row.get('category', ''),
                "budgeted_amount": row.get('budgeted_amount', ''),
                "actual_spend": row.get('actual_spend', ''),
                "notes": row.get('notes', ''),
                "growth_mom": growth.get(row.get('period', ''), 'N/A')
            }
            output_rows.append(output_row)
        
        # Write output CSV with summary rows
        output_fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes", "growth_mom"]
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
            
            # Write summary section
            f.write(f"\n# SUMMARY\n")
            f.write(f"ward,{args.ward}\n")
            f.write(f"category,{args.category}\n")
            f.write(f"total_budgeted,{totals['total_budgeted']}\n")
            f.write(f"total_actual_spend,{totals['total_actual_spend'] if totals['total_actual_spend'] is not None else 'NULL'}\n")
            f.write(f"variance,{totals['variance_display']}\n")
            f.write(f"null_count,{totals['null_count']}\n")
            f.write(f"months_analyzed,{len(totals['months_with_data'])}\n")
        
        print(f"\n✓ Results written to {args.output}")
        print(f"\nSummary:")
        print(f"  Total Budgeted: {totals['total_budgeted']}")
        print(f"  Total Actual Spend: {totals['total_actual_spend'] if totals['total_actual_spend'] is not None else 'NULL (all values are null)'}")
        print(f"  Variance: {totals['variance_display']}")
        print(f"  Null Count: {totals['null_count']}")
        print(f"  Months with Data: {len(totals['months_with_data'])}")
        
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
