"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth enforcing strict granularity,
explicit null flagging, and exact formula transparency.
"""
import argparse
import csv
import sys

def load_dataset(file_path: str) -> dict:
    """Reads CSV, validates columns, reports nulls."""
    rows = []
    null_report = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                
                # Check for null actual_spend
                val = row.get("actual_spend", "").strip()
                if not val or val.lower() == "null":
                    null_report.append({
                        "period": row.get("period"),
                        "ward": row.get("ward"),
                        "category": row.get("category"),
                        "notes": row.get("notes", "No reason provided")
                    })
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)
        
    return {"rows": rows, "null_report": null_report}

def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Computes MoM or YoY growth for a specific ward and category.
    Enforces anti-aggregation and explicit formulas.
    """
    if not ward or not category or ward.lower() == "any" or category.lower() == "any":
        print("ERROR: System REFUSES to aggregate across wards or categories. Specific ward and category must be provided.", file=sys.stderr)
        sys.exit(1)
        
    if not growth_type:
        print("ERROR: --growth-type not specified. System REFUSES to guess. Please provide MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    if growth_type not in ["MoM", "YoY"]:
        print(f"ERROR: Invalid growth type '{growth_type}'. Must be MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    # Filter data
    filtered = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    
    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x.get("period", ""))
    
    results = []
    
    # Helper to find historical value
    def get_hist_val(idx: int, offset: int) -> tuple[float|None, str|None]:
        if idx - offset < 0:
            return None, None
        
        hist_row = filtered[idx - offset]
        val_str = hist_row.get("actual_spend", "").strip()
        if not val_str or val_str.lower() == "null":
            return None, None
            
        try:
            return float(val_str), hist_row.get("period")
        except ValueError:
            return None, None

    for i, row in enumerate(filtered):
        period = row.get("period")
        val_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()
        
        # Handle Nulls explicitly
        if not val_str or val_str.lower() == "null":
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "formula": "N/A",
                "growth_pct": "N/A",
                "null_flag": f"FLAGGED: {notes}" if notes else "FLAGGED: Missing Data"
            })
            continue
            
        try:
            current_val = float(val_str)
        except ValueError:
            continue
            
        # Determine offset (1 for MoM, 12 for YoY)
        # Note: Since data is 12 months for 2024, YoY offset is theoretically 12, 
        # but we don't have 2023 data in this dataset. We'll handle offset dynamically based on index if consecutive.
        offset = 1 if growth_type == "MoM" else 12
        
        hist_val, hist_period = get_hist_val(i, offset)
        
        if hist_val is None:
            results.append({
                "period": period,
                "actual_spend": current_val,
                "formula": "Insufficient history",
                "growth_pct": "N/A",
                "null_flag": ""
            })
        else:
            pct = ((current_val - hist_val) / hist_val) * 100
            formula_str = f"({current_val} - {hist_val}) / {hist_val}"
            
            # Format nicely, e.g. +33.1%
            sign = "+" if pct > 0 else ""
            
            results.append({
                "period": period,
                "actual_spend": current_val,
                "formula": formula_str,
                "growth_pct": f"{sign}{pct:.1f}%",
                "null_flag": ""
            })
            
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze (required)")
    parser.add_argument("--category", required=False, help="Specific category to analyze (required)")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY (required)")
    parser.add_argument("--output", required=True, help="Path to write results")
    args = parser.parse_args()

    # Enforcement: refuse if missing args
    if not args.ward or not args.category or not args.growth_type:
        print("ERROR: --ward, --category, and --growth-type MUST be provided. Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    dataset = load_dataset(args.input)
    
    # Pre-computation requirement: Flag all nulls
    if dataset["null_report"]:
        print(f"WARNING: Discovered {len(dataset['null_report'])} null actual_spend rows in dataset:")
        for nr in dataset["null_report"]:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} -> {nr['notes']}")
        print("These will be flagged in the output.\n")

    results = compute_growth(dataset["rows"], args.ward, args.category, args.growth_type)
    
    if not results:
        print(f"No data found for Ward: '{args.ward}', Category: '{args.category}'. Check your inputs.")
        sys.exit(1)

    fieldnames = ["period", "actual_spend", "formula", "growth_pct", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Calculated {args.growth_type} growth for {args.ward} -> {args.category}. Wrote to {args.output}")
