"""
UC-0C app.py — Safe Financial Growth Calculator
Implements load_dataset and compute_growth to prevent
wrong aggregation levels, silent null handling, and formula assumption.
"""
import argparse
import csv
import sys
import codecs

def load_dataset(file_path: str) -> list[dict]:
    """
    Reads CSV, validates columns, reports null actual_spend rows.
    """
    data = []
    null_count = 0
    try:
        with codecs.open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Flag null actual_spend globally before processing
                if not row.get("actual_spend") or not row["actual_spend"].strip():
                    null_count += 1
                    notes = row.get("notes", "No notes provided")
                    print(f"[WARNING] Null data found: {row['period']} | {row['ward']} | {row['category']} - Reason: {notes}")
                data.append(row)
    except FileNotFoundError:
        print(f"[ERROR] Could not read file: {file_path}")
        sys.exit(1)
        
    if null_count > 0:
        print(f"[INFO] Loaded dataset. {null_count} null actual_spend rows flagged prior to computation.")
    return data

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Filters data precisely, refuses cross-aggregation, computes explicit growth.
    """
    if not ward or not category:
        raise ValueError("Enforcement Error: Never aggregate across wards or categories unless explicitly instructed. Both --ward and --category must be specified.")

    if not growth_type:
        raise ValueError("Enforcement Error: --growth-type must be specified explicitly. Never guess between MoM or YoY.")
        
    if growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError(f"Enforcement Error: Invalid growth_type '{growth_type}'. Must be MoM or YoY.")

    # Filter data
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not filtered:
        print(f"[WARNING] No data found for Ward: '{ward}', Category: '{category}'")
        return []

    # Sort chronologically
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i in range(len(filtered)):
        curr_row = filtered[i]
        period = curr_row["period"]
        actual_spend = curr_row.get("actual_spend", "").strip()
        notes = curr_row.get("notes", "").strip()
        
        # Determine previous index based on growth_type
        prev_idx = i - 1 if growth_type.upper() == "MOM" else i - 12
        
        growth_pct = "NULL"
        formula = ""
        flag = ""
        
        # Handle cases where we cannot compute growth
        if prev_idx < 0:
            formula = "N/A (No prior period)"
            flag = notes
        elif not actual_spend:
            formula = "Missing Data (Current Period)"
            flag = f"NULL FLAGGED: {notes}"
        else:
            prev_spend = filtered[prev_idx].get("actual_spend", "").strip()
            if not prev_spend:
                formula = "Missing Data (Prior Period)"
                flag = f"Prior period NULL FLAGGED"
            else:
                # We have both current and previous spend, compute
                try:
                    curr_val = float(actual_spend)
                    prev_val = float(prev_spend)
                    
                    if prev_val == 0:
                        formula = f"({curr_val} - 0) / 0"
                        growth_pct = "Inf"
                    else:
                        g = ((curr_val - prev_val) / prev_val) * 100
                        
                        # Add plus sign for positive growth, round to 1 decimal
                        if g > 0:
                            growth_pct = f"+{g:.1f}%"
                        else:
                            growth_pct = f"{g:.1f}%"
                            
                        formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                        flag = notes
                except ValueError:
                    formula = "Parse Error"
                    growth_pct = "ERROR"
                    flag = "Non-numeric data"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend if actual_spend else "NULL",
            "growth_pct": growth_pct,
            "formula": formula,
            "flag": flag
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Safe Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to filter")
    parser.add_argument("--category", required=False, help="Specific category to filter")
    parser.add_argument("--growth-type", required=False, help="Calculation type, e.g., MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    
    args = parser.parse_args()

    # Step 1: Load Data
    data = load_dataset(args.input)
    
    # Step 2: Compute
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as ve:
        print(f"[FATAL] {ve}")
        sys.exit(1)
        
    if not results:
        sys.exit(0)
        
    # Step 3: Write Output
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    try:
        with codecs.open(args.output, "w", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Per-period explicit table written to {args.output}")
    except Exception as e:
        print(f"[ERROR] Failed to write to {args.output}: {e}")

if __name__ == "__main__":
    main()
