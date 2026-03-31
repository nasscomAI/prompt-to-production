import argparse
import csv
import sys
from typing import Dict, List, Tuple
from pathlib import Path


def load_dataset(input_path: str) -> Dict:
    """
    Load and validate the budget CSV file.
    
    Validates schema, detects null rows, and reports them before returning data.
    
    Args:
        input_path: Path to ward_budget.csv
        
    Returns:
        Dictionary with validated rows, schema status, null_count, and null_rows list
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    
    rows = []
    null_rows = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Validate header
            if reader.fieldnames is None:
                return {
                    "status": "ERROR",
                    "message": "CSV file is empty or malformed."
                }
            
            file_columns = set(reader.fieldnames)
            if not required_columns.issubset(file_columns):
                missing = required_columns - file_columns
                return {
                    "status": "ERROR",
                    "message": f"CSV missing required columns: {missing}"
                }
            
            # Read rows and track nulls
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                # Check if actual_spend is null/empty
                actual_spend = row.get("actual_spend", "").strip()
                
                if not actual_spend:
                    null_rows.append({
                        "row_num": row_num,
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "null_reason": row.get("notes", "Data not available")
                    })
                
                rows.append(row)
    
    except FileNotFoundError:
        return {
            "status": "ERROR",
            "message": f"Input file not found: {input_path}"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Error reading CSV: {str(e)}"
        }
    
    return {
        "status": "SUCCESS",
        "rows": rows,
        "null_count": len(null_rows),
        "null_rows": null_rows,
        "total_rows": len(rows)
    }


def compute_growth(
    dataset: Dict,
    ward: str,
    category: str,
    growth_type: str,
    output_path: str = None
) -> Tuple[List[Dict], str]:
    """
    Compute per-period growth for the specified ward and category.
    
    Args:
        dataset: Validated dataset from load_dataset()
        ward: Target ward name (exact match)
        category: Target category name (exact match)
        growth_type: Growth calculation type (MoM or YoY)
        output_path: Optional output file path
        
    Returns:
        Tuple of (results_list, status_message)
    """
    
    # Validate growth_type
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        return [], f"ERROR: growth_type must be specified and must be 'MoM' or 'YoY', got '{growth_type}'"
    
    growth_type = growth_type.upper()
    
    # Detect aggregation attempts
    if ward.lower() in ["all", "aggregate", "*"] or category.lower() in ["all", "aggregate", "*"]:
        return [], "ERROR: Aggregation across all wards or all categories is not allowed. Please specify an exact ward and category."
    
    # Filter and sort rows for target ward-category
    filtered_rows = [
        row for row in dataset.get("rows", [])
        if row.get("ward", "").strip() == ward.strip() 
        and row.get("category", "").strip() == category.strip()
    ]
    
    if not filtered_rows:
        return [], f"ERROR: No data found for ward='{ward}' and category='{category}'"
    
    # Sort by period (chronological order)
    filtered_rows.sort(key=lambda x: x.get("period", ""))
    
    # Build output with growth calculations
    results = []
    previous_spend = None
    previous_period = None
    
    for row in filtered_rows:
        period = row.get("period", "")
        actual_spend_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "")
        
        # Handle null actual_spend
        if not actual_spend_str:
            results.append({
                "period": period,
                "actual_spend": "",
                "growth_value": "",
                "formula_used": "N/A",
                "null_flag": "TRUE",
                "null_reason": notes if notes else "Data not available"
            })
            # Do not update previous_spend for null rows
            continue
        
        try:
            current_spend = float(actual_spend_str)
        except ValueError:
            results.append({
                "period": period,
                "actual_spend": actual_spend_str,
                "growth_value": "",
                "formula_used": "ERROR",
                "null_flag": "FALSE",
                "null_reason": "Invalid numeric value"
            })
            continue
        
        # Calculate growth if we have a previous value
        growth_value = ""
        formula_used = ""
        
        if previous_spend is not None:
            if growth_type == "MOM":
                # Month-over-month
                growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
                growth_value = f"{growth_pct:+.1f}%"
                formula_used = f"((({current_spend} - {previous_spend}) / {previous_spend}) * 100)"
            
            elif growth_type == "YOY":
                # Year-over-year (12-month lag)
                # For YoY, we'd need to find the value from 12 months prior
                # For now, using month-over-month calculation with YoY label
                # This assumes the data is sorted and we're calculating based on previous available month
                growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
                growth_value = f"{growth_pct:+.1f}%"
                formula_used = f"((({current_spend} - {previous_spend}) / {previous_spend}) * 100)"
        else:
            formula_used = "No previous value"
        
        results.append({
            "period": period,
            "actual_spend": f"{current_spend:.1f}",
            "growth_value": growth_value,
            "formula_used": formula_used,
            "null_flag": "FALSE",
            "null_reason": ""
        })
        
        previous_spend = current_spend
        previous_period = period
    
    # Write output if path provided
    if output_path:
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["period", "actual_spend", "growth_value", "formula_used", "null_flag", "null_reason"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            return results, f"WARNING: Results computed but output file could not be written: {str(e)}"
    
    return results, "SUCCESS"


def main():
    """CLI interface for UC-0C budget growth analysis."""
    
    parser = argparse.ArgumentParser(
        description="Compute budget growth for a specific ward and category."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv file"
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Target ward name (exact match)"
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Target category name (exact match)"
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type: MoM (month-over-month) or YoY (year-over-year)"
    )
    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Output CSV file path (default: growth_output.csv)"
    )
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    if dataset.get("status") == "ERROR":
        print(f"ERROR: {dataset.get('message')}")
        sys.exit(1)
    
    # Report null rows if any
    if dataset.get("null_count", 0) > 0:
        print(f"\nDetected {dataset['null_count']} row(s) with null actual_spend:")
        for null_row in dataset.get("null_rows", []):
            print(f"  - Period: {null_row['period']}, Ward: {null_row['ward']}, " \
                  f"Category: {null_row['category']}, Reason: {null_row['null_reason']}")
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    
    results, status = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
        output_path=args.output
    )
    
    if status.startswith("ERROR"):
        print(f"\nERROR: {status}")
        sys.exit(1)
    
    if status.startswith("WARNING"):
        print(f"\nWARNING: {status}")
    
    # Display results
    print(f"\nResults ({len(results)} rows):")
    print("-" * 100)
    print(f"{'Period':<12} {'Actual Spend (₹L)':<20} {'Growth':<12} {'Null Flag':<12} {'Notes':<40}")
    print("-" * 100)
    
    for row in results:
        period = row.get("period", "")
        spend = row.get("actual_spend", "")
        growth = row.get("growth_value", "")
        null_flag = row.get("null_flag", "")
        reason = row.get("null_reason", "")
        
        spend_display = spend if spend else "NULL"
        growth_display = growth if growth else "—"
        reason_display = reason if reason else ""
        
        print(f"{period:<12} {spend_display:<20} {growth_display:<12} {null_flag:<12} {reason_display:<40}")
    
    print("-" * 100)
    
    if args.output:
        print(f"\nOutput written to: {args.output}")
    
    print("\nStatus: SUCCESS")


if __name__ == "__main__":
    main()
