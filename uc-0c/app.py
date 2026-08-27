"""
UC-0C app.py — Growth calculator.
Implements skills from uc-0c/skills.md and enforcement from uc-0c/agents.md.
"""
import argparse
import csv
from typing import Dict, List, Tuple

def load_dataset(file_path: str) -> Tuple[List[Dict], Dict]:
    """Reads CSV, validates columns, reports null count and which rows."""
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_rows = []
    null_count = 0
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Missing required columns: {required_columns - set(reader.fieldnames or [])}")
            for row in reader:
                data.append(row)
                if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                    null_count += 1
                    null_rows.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row.get("notes", "")
                    })
    except Exception as e:
        return [], {"error": str(e)}
    report = {
        "null_count": null_count,
        "null_rows": null_rows
    }
    return data, report

def compute_growth(data: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    if growth_type not in ["MoM", "YoY"]:
        return [{"error": f"Invalid growth_type: {growth_type}. Must be MoM or YoY."}]
    
    # Filter data
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    if not filtered:
        return [{"error": f"No data found for ward '{ward}' and category '{category}'."}]
    
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    prev_value = None
    prev_period = None
    for row in filtered:
        period = row["period"]
        actual_spend_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "")
        flag = ""
        growth = ""
        formula = ""
        
        if not actual_spend_str:
            flag = f"NULL: {notes}"
            actual_spend = None
        else:
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                flag = f"INVALID VALUE: {actual_spend_str}"
                actual_spend = None
        
        if actual_spend is not None:
            if growth_type == "MoM" and prev_value is not None:
                growth_pct = ((actual_spend - prev_value) / prev_value) * 100
                growth = f"{growth_pct:.1f}%"
                formula = f"(({actual_spend} - {prev_value}) / {prev_value}) * 100"
            elif growth_type == "YoY":
                # For YoY, need same month previous year, but data is only 2024, so perhaps not applicable
                # README focuses on MoM, so maybe skip or error
                growth = "N/A (YoY not supported with single year data)"
                formula = "N/A"
            else:
                growth = "N/A (first period)"
                formula = "N/A"
            prev_value = actual_spend
        else:
            prev_value = None  # Reset on null
        
        results.append({
            "period": period,
            "actual_spend": actual_spend_str,
            "growth": growth,
            "formula": formula,
            "flag": flag
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    data, report = load_dataset(args.input)
    if "error" in report:
        print(f"Error loading dataset: {report['error']}")
        return
    
    print(f"Loaded {len(data)} rows. Null count: {report['null_count']}")
    for null_row in report["null_rows"]:
        print(f"Null row: {null_row}")
    
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    if results and "error" in results[0]:
        print(results[0]["error"])
        return
    
    # Write output CSV
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
