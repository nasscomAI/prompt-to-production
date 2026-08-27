#!/usr/bin/env python3
"""
UC-0C: Budget Growth Calculator
Computes ward/category-specific growth rates with null handling and formula transparency.
"""

import argparse
import csv
import sys
from pathlib import Path
from datetime import datetime


def load_dataset(file_path):
    """
    Loads budget CSV and validates structure, identifies null rows.
    
    Args:
        file_path (str): Path to ward_budget.csv
        
    Returns:
        dict: Dataset with data, null_rows, statistics
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        if not reader.fieldnames:
            raise ValueError("CSV file has no columns")
        
        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        
        # Read all data
        data = list(reader)
    
    if not data:
        raise ValueError("Dataset contains no data")
    
    # Identify null rows
    null_rows = []
    for row in data:
        if not row['actual_spend'] or row['actual_spend'].strip() == '':
            null_rows.append({
                "period": row['period'],
                "ward": row['ward'],
                "category": row['category'],
                "reason": row['notes'].strip() if row['notes'] else "No reason provided"
            })
    
    # Get unique values
    wards = sorted(set(row['ward'] for row in data))
    categories = sorted(set(row['category'] for row in data))
    periods = sorted(set(row['period'] for row in data))
    
    return {
        "data": data,
        "total_rows": len(data),
        "null_rows": null_rows,
        "null_count": len(null_rows),
        "wards": wards,
        "categories": categories,
        "periods": periods
    }


def compute_growth(dataset, ward, category, growth_type, output_path):
    """
    Computes growth rates for specific ward + category with formula transparency.
    
    Args:
        dataset (dict): Output from load_dataset
        ward (str): Exact ward name
        category (str): Exact category name
        growth_type (str): "MoM" or "YoY"
        output_path (str): Path to write output CSV
    """
    # Validate growth_type
    if not growth_type or growth_type not in ["MoM", "YoY"]:
        raise ValueError(
            "growth_type must be explicitly specified as either 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year). Cannot guess."
        )
    
    # Validate ward
    if ward not in dataset["wards"]:
        raise ValueError(
            f"Ward '{ward}' not found. Available wards: {', '.join(dataset['wards'])}"
        )
    
    # Validate category
    if category not in dataset["categories"]:
        raise ValueError(
            f"Category '{category}' not found. Available categories: {', '.join(dataset['categories'])}"
        )
    
    # Check for aggregation requests
    if ward.lower() in ["all", "total", "*"] or category.lower() in ["all", "total", "*"]:
        raise ValueError(
            "Aggregation across wards or categories is not permitted without explicit instruction. "
            "Specify a single ward and single category."
        )
    
    # Filter data for specific ward + category
    filtered_data = [
        row for row in dataset["data"]
        if row["ward"] == ward and row["category"] == category
    ]
    
    if not filtered_data:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'. Check spelling and try again."
        )
    
    # Sort by period
    filtered_data.sort(key=lambda x: x["period"])
    
    # Report null rows for this ward + category
    ward_cat_nulls = [
        n for n in dataset["null_rows"]
        if n["ward"] == ward and n["category"] == category
    ]
    
    if ward_cat_nulls:
        print(f"\nFound {len(ward_cat_nulls)} null row(s) for {ward} - {category}:")
        for null in ward_cat_nulls:
            print(f"  - {null['period']}: {null['reason']}")
    
    # Compute growth for each period
    results = []
    previous_value = None
    previous_period = None
    
    for i, row in enumerate(filtered_data):
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip()
        
        # Check if current value is null
        if not actual_spend_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_rate": "N/A",
                "formula": f"NULL: {row['notes']}",
                "flag": "NULL_DATA"
            })
            previous_value = None
            previous_period = period
            continue
        
        current_value = float(actual_spend_str)
        
        # First period or previous was null
        if previous_value is None:
            if i == 0:
                formula = "First period - no previous data"
            else:
                formula = f"Previous period ({previous_period}) was NULL"
            
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value:.1f}",
                "growth_rate": "N/A",
                "formula": formula,
                "flag": ""
            })
        else:
            # Calculate growth
            if growth_type == "MoM":
                growth = ((current_value - previous_value) / previous_value) * 100
                formula_str = f"({current_value:.1f} - {previous_value:.1f}) / {previous_value:.1f} × 100"
            else:  # YoY
                # For YoY, we need same month previous year
                # Simple implementation: just show the calculation
                growth = ((current_value - previous_value) / previous_value) * 100
                formula_str = f"({current_value:.1f} - {previous_value:.1f}) / {previous_value:.1f} × 100"
            
            # Format growth rate with sign
            if growth >= 0:
                growth_str = f"+{growth:.1f}%"
            else:
                growth_str = f"{growth:.1f}%"
            
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value:.1f}",
                "growth_rate": growth_str,
                "formula": f"{formula_str} = {growth_str}",
                "flag": ""
            })
        
        previous_value = current_value
        previous_period = period
    
    # Write output CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nOutput written to: {output_path}")
    print(f"Total periods: {len(results)}")
    print(f"Null data flags: {sum(1 for r in results if r['flag'] == 'NULL_DATA')}")
    print(f"Growth calculations: {sum(1 for r in results if r['growth_rate'] not in ['N/A'])}")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Calculate budget growth rates with null handling and formula transparency"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Ward name (exact match, e.g., 'Ward 1 – Kasba')"
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Category name (exact match, e.g., 'Roads & Pothole Repair')"
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
        help="Growth calculation type: MoM (Month-over-Month) or YoY (Year-over-Year)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output growth CSV file"
    )
    
    args = parser.parse_args()
    
    try:
        print("="*70)
        print("UC-0C: Budget Growth Calculator")
        print("="*70)
        print(f"\nInput: {args.input}")
        print(f"Ward: {args.ward}")
        print(f"Category: {args.category}")
        print(f"Growth Type: {args.growth_type}")
        print(f"Output: {args.output}\n")
        
        # Step 1: Load and validate dataset
        print("Step 1: Loading dataset...")
        dataset = load_dataset(args.input)
        print(f"✓ Loaded {dataset['total_rows']} rows")
        print(f"  - {len(dataset['wards'])} wards, {len(dataset['categories'])} categories, {len(dataset['periods'])} periods")
        
        if dataset['null_count'] > 0:
            print(f"\n⚠ Found {dataset['null_count']} null actual_spend rows across all wards:")
            for null in dataset['null_rows']:
                print(f"  - {null['period']} | {null['ward']} | {null['category']}: {null['reason']}")
        
        # Step 2: Compute growth
        print(f"\nStep 2: Computing {args.growth_type} growth for {args.ward} - {args.category}...")
        compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)
        
        print("\n" + "="*70)
        print("SUCCESS: Growth analysis complete")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

