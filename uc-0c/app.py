"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from typing import List, Dict, Any

def load_dataset(file_path: str) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    Returns: (dataset, null_rows)
    """
    expected_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    dataset = []
    null_rows = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames != expected_columns:
                raise ValueError(f"Expected columns: {expected_columns}, got: {reader.fieldnames}")
            for i, row in enumerate(reader):
                if row["actual_spend"] == '' or row["actual_spend"] is None:
                    null_rows.append({"row": i+2, "reason": row["notes"], "data": row})
                dataset.append(row)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    return dataset, null_rows

def compute_growth(dataset: List[Dict[str, Any]], ward: str, category: str, growth_type: str) -> List[Dict[str, Any]]:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Flags rows with null spend.
    """
    # Filter dataset
    filtered = [row for row in dataset if row["ward"] == ward and row["category"] == category]
    if not filtered:
        print(f"ERROR: No data found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        sys.exit(1)
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    results = []
    prev_spend = None
    prev_period = None
    for row in filtered:
        period = row["period"]
        actual_spend = row["actual_spend"]
        note = row["notes"]
        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend,
            "formula": "",
            "growth": "",
            "flag": ""
        }
        if actual_spend == '' or actual_spend is None:
            result["flag"] = f"NULL: {note}"
            result["growth"] = ""
            result["formula"] = "N/A"
        else:
            try:
                actual_spend_val = float(actual_spend)
            except Exception:
                result["flag"] = "INVALID actual_spend"
                actual_spend_val = None
            if prev_spend is not None and actual_spend_val is not None:
                if growth_type == "MoM":
                    formula = f"({actual_spend_val} - {prev_spend}) / {prev_spend}"
                    try:
                        growth = (actual_spend_val - prev_spend) / prev_spend if prev_spend != 0 else None
                    except Exception:
                        growth = None
                    result["growth"] = f"{growth:.4f}" if growth is not None else "DIV/0"
                    result["formula"] = formula
                elif growth_type == "YoY":
                    # For this dataset, YoY only makes sense if there are multiple years
                    result["growth"] = "N/A"
                    result["formula"] = "YoY not implemented (single year dataset)"
                else:
                    print(f"ERROR: Unsupported growth_type '{growth_type}'.", file=sys.stderr)
                    sys.exit(1)
            else:
                result["growth"] = ""
                result["formula"] = "N/A (no previous period)"
            prev_spend = actual_spend_val
            prev_period = period
        results.append(result)
    return results

def write_output(results: List[Dict[str, Any]], output_path: str):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Metric Agent")
    parser.add_argument('--input', required=True, help='Path to input CSV dataset')
    parser.add_argument('--ward', required=True, help='Ward name (string)')
    parser.add_argument('--category', required=True, help='Category name (string)')
    parser.add_argument('--growth-type', required=True, help='Growth type (e.g., MoM, YoY)')
    parser.add_argument('--output', required=True, help='Path to output CSV file')
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if not args.growth_type:
        print("Refusal: --growth-type must be specified.", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    dataset, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"INFO: {len(null_rows)} rows with null actual_spend. See output for flags.")

    # Enforcement: never aggregate across wards/categories
    # (Handled by filtering in compute_growth)

    # Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output
    write_output(results, args.output)
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
