"""
UC-0C app.py — Budget Growth Calculator
Computes MoM/YoY growth with explicit null flagging and formula transparency.
"""
import argparse
import csv
from typing import Dict, List


def load_dataset(input_path: str) -> Dict:
    """
    Load budget CSV and identify all null actual_spend rows before processing.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV: {e}")
    
    if not rows:
        raise ValueError("CSV is empty")
    
    # Validate required columns
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    first_row = rows[0]
    missing_cols = [col for col in required_cols if col not in first_row]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Identify null rows
    null_rows = []
    for row in rows:
        actual_spend = row["actual_spend"].strip() if row["actual_spend"] else ""
        if not actual_spend or actual_spend.lower() == "nan":
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"] if row["notes"] else "No reason provided"
            })
    
    print(f"Dataset loaded. Found {len(null_rows)} null actual_spend rows:")
    for null_row in null_rows:
        print(f"  {null_row['period']} | {null_row['ward']} | {null_row['category']} | {null_row['reason']}")
    
    return {
        "data": rows,
        "null_rows": null_rows,
        "total_nulls": len(null_rows)
    }


def compute_growth(dataset: Dict, ward: str, category: str, growth_type: str, output_path: str = None):
    """
    Compute growth for a single ward-category pair.
    growth_type: 'MoM' (month-over-month) or 'YoY' (year-over-year)
    """
    rows = dataset["data"]
    
    # Validate parameters
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("Specify growth type: MoM (month-over-month) or YoY (year-over-year)")
    
    # Filter by ward and category
    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    
    if not filtered:
        raise ValueError(f"No data found for Ward: '{ward}', Category: '{category}'")
    
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    # Build output rows
    output_rows = []
    prev_spend = None
    prev_period = None
    
    for row in filtered:
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip() if row["actual_spend"] else ""
        
        # Check if this is a null row
        is_null = not actual_spend_str or actual_spend_str.lower() == "nan"
        
        if is_null:
            reason = row["notes"] if row["notes"] else "No data"
            output_rows.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_period_spend": prev_spend if prev_spend else "N/A",
                "formula": "N/A",
                "growth_percent": f"NULL — {reason}"
            })
        else:
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                output_rows.append({
                    "period": period,
                    "actual_spend": "ERROR",
                    "previous_period_spend": "N/A",
                    "formula": "N/A",
                    "growth_percent": "Invalid number"
                })
                continue
            
            if growth_type == "MoM" and prev_spend is not None:
                # Month-over-month growth
                growth = ((actual_spend - prev_spend) / prev_spend) * 100
                formula = f"({actual_spend:.1f}-{prev_spend:.1f})/{prev_spend:.1f} × 100"
                output_rows.append({
                    "period": period,
                    "actual_spend": f"{actual_spend:.1f}",
                    "previous_period_spend": f"{prev_spend:.1f}",
                    "formula": formula,
                    "growth_percent": f"{growth:+.1f}%"
                })
            elif growth_type == "YoY":
                # Year-over-year growth - look back 12 months
                current_year = int(period[:4])
                current_month = period[5:]
                yoy_period = f"{current_year - 1}-{current_month}"
                
                yoy_row = next((r for r in filtered if r["period"] == yoy_period), None)
                
                if yoy_row:
                    yoy_spend_str = yoy_row["actual_spend"].strip() if yoy_row["actual_spend"] else ""
                    if yoy_spend_str and yoy_spend_str.lower() != "nan":
                        try:
                            yoy_spend = float(yoy_spend_str)
                            growth = ((actual_spend - yoy_spend) / yoy_spend) * 100
                            formula = f"({actual_spend:.1f}-{yoy_spend:.1f})/{yoy_spend:.1f} × 100"
                            output_rows.append({
                                "period": period,
                                "actual_spend": f"{actual_spend:.1f}",
                                "previous_period_spend": f"{yoy_spend:.1f}",
                                "formula": formula,
                                "growth_percent": f"{growth:+.1f}%"
                            })
                        except ValueError:
                            output_rows.append({
                                "period": period,
                                "actual_spend": f"{actual_spend:.1f}",
                                "previous_period_spend": "INVALID",
                                "formula": "N/A",
                                "growth_percent": "N/A (prior year invalid)"
                            })
                    else:
                        output_rows.append({
                            "period": period,
                            "actual_spend": f"{actual_spend:.1f}",
                            "previous_period_spend": "NULL",
                            "formula": "N/A",
                            "growth_percent": "N/A (prior year null)"
                        })
                else:
                    output_rows.append({
                        "period": period,
                        "actual_spend": f"{actual_spend:.1f}",
                        "previous_period_spend": "N/A",
                        "formula": "N/A",
                        "growth_percent": "N/A (first year)"
                    })
            else:
                # First row in MoM mode
                output_rows.append({
                    "period": period,
                    "actual_spend": f"{actual_spend:.1f}",
                    "previous_period_spend": "N/A",
                    "formula": "N/A",
                    "growth_percent": "N/A (baseline)"
                })
            
            prev_spend = actual_spend
            prev_period = period
    
    # Write output
    if output_path:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "previous_period_spend", "formula", "growth_percent"])
            writer.writeheader()
            writer.writerows(output_rows)
        print(f"Growth calculation written to {output_path}")
    else:
        # Print to stdout
        for row in output_rows:
            print(f"{row['period']} | Spend: {row['actual_spend']} | Prev: {row['previous_period_spend']} | Growth: {row['growth_percent']}")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator - Single ward-category only, with formula transparency"
    )
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name (required)")
    parser.add_argument("--category", required=True, help="Category name (required)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=False, help="Path to write results CSV")
    
    args = parser.parse_args()
    
    try:
        # Load and flag nulls
        dataset = load_dataset(args.input)
        print()
        
        # Compute growth
        compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)
    
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
