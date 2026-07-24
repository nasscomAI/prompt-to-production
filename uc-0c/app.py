"""
UC-0C — Budget Growth Calculator
Implements growth rate computation following RICE enforcement rules.

Core failure modes addressed:
- Wrong aggregation level: Never aggregate across wards/categories without explicit instruction
- Silent null handling: Flag every null before computing
- Formula assumption: Always show formula, refuse if growth-type not specified
"""
import argparse
import csv
from typing import Optional


def load_dataset(input_path: str) -> dict:
    """
    Load budget CSV and validate structure, reporting nulls.
    
    Args:
        input_path: Path to CSV file
        
    Returns:
        Dictionary with data, null_report, wards, categories, periods
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if reader.fieldnames is None:
                raise ValueError("CSV file appears to be empty")
            
            missing = [col for col in required_columns if col not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            data = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {input_path}")
    
    # Parse and identify nulls
    null_report = []
    wards = set()
    categories = set()
    periods = set()
    
    for row in data:
        wards.add(row["ward"])
        categories.add(row["category"])
        periods.add(row["period"])
        
        # Check for null actual_spend
        actual = row.get("actual_spend", "").strip()
        if actual == "" or actual.lower() == "null":
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "No reason provided").strip() or "No reason provided"
            })
    
    return {
        "data": data,
        "null_report": null_report,
        "wards": sorted(list(wards)),
        "categories": sorted(list(categories)),
        "periods": sorted(list(periods))
    }


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute growth rates for specific ward+category.
    
    Args:
        data: List of row dictionaries from load_dataset
        ward: Ward name (must match exactly)
        category: Category name (must match exactly)
        growth_type: 'MoM' for month-over-month
        
    Returns:
        List of dictionaries with period, actual_spend, previous_spend, growth_rate, formula
    """
    # Filter data for specific ward+category
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]
    
    if not filtered:
        # Check if ward or category exists
        all_wards = set(row["ward"] for row in data)
        all_categories = set(row["category"] for row in data)
        
        if ward not in all_wards:
            raise ValueError(f"Ward '{ward}' not found. Valid wards: {sorted(all_wards)}")
        if category not in all_categories:
            raise ValueError(f"Category '{category}' not found. Valid categories: {sorted(all_categories)}")
        
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")
    
    # Sort by period
    filtered = sorted(filtered, key=lambda x: x["period"])
    
    # Compute growth rates
    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        
        # Parse actual spend (handle nulls)
        actual_str = row.get("actual_spend", "").strip()
        if actual_str == "" or actual_str.lower() == "null":
            actual = None
            actual_display = "NULL"
        else:
            actual = float(actual_str)
            actual_display = f"{actual:.1f}"
        
        # Get previous value for MoM
        if growth_type == "MoM":
            if i == 0:
                # First period - no previous
                results.append({
                    "period": period,
                    "actual_spend": actual_display,
                    "previous_spend": "N/A (first period)",
                    "growth_rate": "N/A (first period)",
                    "formula": "N/A (first period)"
                })
                continue
            
            prev_row = filtered[i - 1]
            prev_str = prev_row.get("actual_spend", "").strip()
            if prev_str == "" or prev_str.lower() == "null":
                prev = None
                prev_display = "NULL"
            else:
                prev = float(prev_str)
                prev_display = f"{prev:.1f}"
        
        elif growth_type == "YoY":
            # Find same month previous year
            target_period = period[:4]  # Get year
            target_year = int(target_period) - 1
            target_month = period[5:]  # Get month
            prev_period = f"{target_year}-{target_month}"
            
            prev_rows = [r for r in filtered if r["period"] == prev_period]
            if not prev_rows:
                results.append({
                    "period": period,
                    "actual_spend": actual_display,
                    "previous_spend": "N/A (no previous year)",
                    "growth_rate": "N/A (no previous year data)",
                    "formula": "N/A (no previous year data)"
                })
                continue
            
            prev_row = prev_rows[0]
            prev_str = prev_row.get("actual_spend", "").strip()
            if prev_str == "" or prev_str.lower() == "null":
                prev = None
                prev_display = "NULL"
            else:
                prev = float(prev_str)
                prev_display = f"{prev:.1f}"
        else:
            raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")
        
        # Compute growth rate
        if actual is None or prev is None:
            growth_rate = "N/A - NULL VALUE"
            formula = f"Cannot compute: {'current' if actual is None else 'previous'} value is NULL"
        elif prev == 0:
            growth_rate = "N/A - Division by zero"
            formula = f"({actual_display} - 0) / 0 * 100 = undefined"
        else:
            growth = ((actual - prev) / prev) * 100
            growth_rate = f"{growth:+.1f}%"
            formula = f"({actual_display} - {prev_display}) / {prev_display} * 100 = {growth:+.1f}%"
        
        results.append({
            "period": period,
            "actual_spend": actual_display,
            "previous_spend": prev_display,
            "growth_rate": growth_rate,
            "formula": formula
        })
    
    return results


def main():
    """Main entry point for budget growth calculator."""
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", dest="growth_type", required=True, 
                        choices=["MoM", "YoY"], help="Growth calculation type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    # Load and validate dataset
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    # Report nulls BEFORE computing
    print(f"\n{'='*60}")
    print("NULL VALUE REPORT")
    print(f"{'='*60}")
    if dataset["null_report"]:
        print(f"Found {len(dataset['null_report'])} null actual_spend values:")
        for null_row in dataset["null_report"]:
            print(f"  - {null_row['period']} | {null_row['ward']} | {null_row['category']}")
            print(f"    Reason: {null_row['reason']}")
    else:
        print("No null values found.")
    print(f"{'='*60}\n")
    
    # Compute growth
    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    print()
    
    results = compute_growth(
        data=dataset["data"],
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )
    
    # Write output CSV
    fieldnames = ["period", "actual_spend", "previous_spend", "growth_rate", "formula"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Also print to console
    print(f"{'='*60}")
    print("GROWTH CALCULATION RESULTS")
    print(f"{'='*60}")
    print(f"{'Period':<10} {'Actual':<10} {'Previous':<12} {'Growth':<15} Formula")
    print("-" * 80)
    for row in results:
        print(f"{row['period']:<10} {row['actual_spend']:<10} {row['previous_spend']:<12} {row['growth_rate']:<15} {row['formula'][:40]}")
    
    print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()
