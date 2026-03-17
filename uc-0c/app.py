"""
UC-0C — Number That Looks Right
Built from agents.md (RICE) and skills.md skill contracts.

Agent role   : Budget growth calculator — calculates MoM/YoY growth.
               Never aggregates across wards/categories unless instructed.
Agent intent : Produce per-ward, per-category growth table. Every computed
               row shows its formula. Null values are flagged with reasons
               from the notes column, not coerced to zero or silently ignored.
Agent context: Only the provided budget data CSV is used.
"""

import argparse
import csv
import sys
from typing import Optional, List, Dict, Tuple, cast

def load_dataset(file_path: str) -> Tuple[List[Dict[str, Optional[str | float]]], dict]:
    """
    Reads a CSV file, validates columns, and reports any null values in actual_spend.

    Returns:
        tuple: (list of row dicts, metadata dict with null analysis)
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data: List[Dict[str, Optional[str | float]]] = []
    
    null_count = 0
    null_indices = []

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing_cols = required_cols - set(fieldnames)
            if missing_cols:
                raise ValueError(
                    f"Missing required columns: {missing_cols}. "
                    f"Found: {fieldnames}"
                )
            
            for i, row in enumerate(reader, start=2): # 1-based header, data starts at 2
                # Standardize nulls
                val = str(row.get("actual_spend", "")).strip()
                if val == "":
                    row["actual_spend"] = None
                    null_count += 1
                    null_indices.append(i)
                else:
                    try:
                        row["actual_spend"] = float(val)
                    except ValueError:
                         row["actual_spend"] = None
                         null_count += 1
                         null_indices.append(i)
                
                data.append(row) # type: ignore

    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found at: {file_path}")

    metadata = {
        "total_rows": len(data),
        "null_count": null_count,
        "null_rows": null_indices
    }
    
    return data, metadata


def compute_growth(data: List[Dict[str, Optional[str | float]]], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Calculates MoM or YoY growth for a specific ward and category.
    
    Enforces rules:
    - Never aggregates across all wards (ward must be specified).
    - Never aggregates across all categories (category must be specified).
    - Requires valid growth_type.
    - Explicitly shows formula.
    - Flags null values and reasons instead of computing growth.
    """
    if not growth_type or growth_type not in ("MoM", "YoY"):
        raise ValueError("growth_type must be explicitly specified as 'MoM' or 'YoY'. Cannot guess.")
        
    if not ward or ward.lower() == "all" or not category or category.lower() == "all":
         raise ValueError(
             "Refusing request: Cannot aggregate across all wards or categories "
             "unless explicitly instructed via specialised workflows. Please "
             "specify a single target ward and category."
         )

    # Filter data
    filtered = [row for row in data if row.get("ward") == ward and row.get("category") == category]
    
    # Sort chronologically (YYYY-MM string sorting works)
    filtered.sort(key=lambda x: str(x.get("period", "")))

    if not filtered:
        return []

    results = []
    
    # Growth offset: MoM = 1 month prior, YoY = 12 months prior
    offset: int = 1 if growth_type == "MoM" else 12

    for i in range(len(filtered)):
        curr_row = filtered[i]
        curr_period = curr_row.get("period")
        curr_spend_val = curr_row.get("actual_spend")
        
        output_row = {
            "period": curr_period,
            "ward": curr_row.get("ward"),
            "category": curr_row.get("category"),
            "actual_spend": curr_spend_val,
            "growth_type": growth_type,
            "growth_pct": None,
            "formula": "None",
            "flag": ""
        }

        # Rule 2: Flag missing values immediately
        if curr_spend_val is None:
            output_row["flag"] = f"NULL DETECTED: {curr_row.get('notes', '')}"
            output_row["formula"] = "Cannot compute: current period actual_spend is null"
            results.append(output_row)
            continue

        if i < offset:
            output_row["formula"] = "Insufficient history for calculation"
            results.append(output_row)
            continue
            
        idx: int = int(i) - int(offset)
        prev_row = filtered[idx]
        prev_spend_val = prev_row.get("actual_spend")
        
        if prev_spend_val is None:
            output_row["flag"] = f"CANNOT COMPUTE: Previous period ({prev_row.get('period')}) is null ({prev_row.get('notes', '')})"
            output_row["formula"] = f"({curr_spend_val} - NULL) / NULL"
            results.append(output_row)
            continue

        # Narrow types for the type checker completely safely
        if isinstance(curr_spend_val, (int, float)):
            curr_spend = float(curr_spend_val)
        else:
            curr_spend = float(str(curr_spend_val))

        if isinstance(prev_spend_val, (int, float)):
            prev_spend = float(prev_spend_val)
        else:
            prev_spend = float(str(prev_spend_val))

        # Valid compute
        if prev_spend == 0.0:
            output_row["formula"] = f"({curr_spend} - {prev_spend}) / {prev_spend} (Div by Zero)"
            output_row["flag"] = "MATH ERROR: Previous spend was exactly 0"
        else:
            diff = curr_spend - prev_spend
            growth = float((diff / prev_spend) * 100.0)
            output_row["growth_pct"] = round(growth, 1)  # type: ignore
            # Rule 3: Show explicit formula used
            output_row["formula"] = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100 = {output_row['growth_pct']}%"
            
        results.append(output_row)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=False, help="Must be MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()

    # Enforcement rule 4: Refuse and ask if growth type is not provided.
    if not args.growth_type:
        print("ERROR: --growth-type not specified. Refusing to guess. Please provide MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading dataset from: {args.input}")
    try:
        data, metadata = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading data: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Dataset loaded. Total rows: {metadata['total_rows']}. Null actual_spend detected: {metadata['null_count']}.")

    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"AGENT REFUSAL: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print(f"Warning: No data found for ward '{args.ward}' and category '{args.category}'.", file=sys.stderr)

    output_cols = ["period", "ward", "category", "actual_spend", "growth_type", "growth_pct", "formula", "flag"]
    
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_cols)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Output written to {args.output}")


if __name__ == "__main__":
    main()
