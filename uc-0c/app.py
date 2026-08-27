"""
UC-0C — Budget Growth Analyzer
Production-grade implementation featuring strict constraint enforcement,
explicit formula tracking, and deliberate null-handling guardrails.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """Reads the CSV dataset, preserves column types, and explicitly catches null values."""
    if not os.path.exists(input_path):
        print(f"Error: Dataset file not found at '{input_path}'", file=sys.stderr)
        sys.exit(1)
        
    rows = []
    with open(input_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            actual_raw = row.get("actual_spend", "").strip()
            if actual_raw == "" or actual_raw.upper() == "NULL":
                row["actual_spend"] = None
            else:
                try:
                    row["actual_spend"] = float(actual_raw)
                except ValueError:
                    row["actual_spend"] = None
            rows.append(row)
    return rows

def compute_growth(rows: list, target_ward: str, target_category: str, growth_type: str) -> list:
    """Filters data and calculates growth metrics tracking results across explicit schema data fields."""
    filtered_rows = [r for r in rows if r["ward"] == target_ward and r["category"] == target_category]
    filtered_rows.sort(key=lambda x: x["period"])
    
    if not filtered_rows:
        print(f"Error: No data records match ward '{target_ward}' and category '{target_category}'", file=sys.stderr)
        sys.exit(1)
        
    computed_table = []
    g_type_upper = growth_type.upper()
    
    for i, current_row in enumerate(filtered_rows):
        period = current_row["period"]
        current_spend = current_row["actual_spend"]
        notes = current_row.get("notes", "").strip()
        
        # Base schema payload template without empty trailing positions
        out_row = {
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": "NULL" if current_spend is None else f"{current_spend:.1f}",
            "growth_type": g_type_upper,
            "growth_percent": "n/a",
            "formula": "n/a",
            "status": "OK",
            "null_reason": "None"
        }
        
        # Guard against deliberate null values explicitly
        if current_spend is None:
            out_row["status"] = "DATA_NULL"
            out_row["null_reason"] = notes if notes else "Data unrecorded"
            computed_table.append(out_row)
            continue

        if g_type_upper == "MOM":
            if i == 0:
                out_row["formula"] = "MoM = (current - previous) / previous * 100"
                out_row["status"] = "NO_PREVIOUS_PERIOD"
            else:
                prev_spend = filtered_rows[i - 1]["actual_spend"]
                if prev_spend is None:
                    out_row["status"] = "PREVIOUS_PERIOD_NULL"
                    out_row["null_reason"] = "Cannot compute metric because the previous period spend value was missing"
                else:
                    pct = ((current_spend - prev_spend) / prev_spend) * 100
                    out_row["growth_percent"] = f"{pct:.1f}"
                    out_row["formula"] = f"(({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                    
        elif g_type_upper == "YTD":
            base_spend = filtered_rows[0]["actual_spend"]
            if base_spend is None:
                out_row["status"] = "BASE_PERIOD_NULL"
                out_row["null_reason"] = "Cannot compute YTD metric because the initial baseline month spend value was missing"
            elif i == 0:
                out_row["growth_percent"] = "0.0"
                out_row["formula"] = "Base month baseline marker"
                out_row["status"] = "BASE_PERIOD"
            else:
                pct = ((current_spend - base_spend) / base_spend) * 100
                out_row["growth_percent"] = f"{pct:.1f}"
                out_row["formula"] = f"(({current_spend:.1f} - {base_spend:.1f}) / {base_spend:.1f}) * 100"
                
        computed_table.append(out_row)
    return computed_table

def write_results(output_path: str, dataset: list):
    """Saves verified clean tabular matrix into output destination."""
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "growth_percent", "formula", "status", "null_reason"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target operating category")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YTD", "mom", "ytd"], help="Growth type calculation method")
    parser.add_argument("--output", required=True, help="Path to save growth_output.csv")
    args = parser.parse_args()

    raw_data = load_dataset(args.input)
    analysis_results = compute_growth(raw_data, args.ward, args.category, args.growth_type)
    write_results(args.output, analysis_results)
    print(f"Done. Clean metrics table written to {args.output}")