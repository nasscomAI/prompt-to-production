import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads CSV, validates columns, reports null count and which rows.
    Returns dataset.
    """
    expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames if reader.fieldnames else [])
            if not expected_cols.issubset(headers):
                print(f"Error: Missing expected columns. Expected {expected_cols}, got {headers}")
                sys.exit(1)
                
            for idx, row in enumerate(reader, start=2): # +1 for 1-based, +1 for header
                data.append(row)
                if not row.get("actual_spend") or row.get("actual_spend").strip() == "":
                    null_rows.append((idx, row.get("ward"), row.get("category"), row.get("period"), row.get("notes")))
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f"\n[ALERT] Found {len(null_rows)} deliberately null 'actual_spend' values:")
        for r in null_rows:
            print(f"  - Row {r[0]} | {r[3]} · {r[1]} · {r[2]} | Note: {r[4]}")
        print("-" * 50)
        
    return data

def compute_growth(dataset, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Never aggregates.
    """
    if str(ward).lower() == "all" or str(category).lower() == "all":
        print("Error: Aggregation across wards or categories is strictly forbidden.")
        sys.exit(1)
        
    filtered = [row for row in dataset if row["ward"] == ward and row["category"] == category]
    
    if not filtered:
        print(f"No data found for Ward: '{ward}', Category: '{category}'")
        return []
        
    # Chronological sort needed for MoM/YoY based on 'period'
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current["period"]
        actual_str = current["actual_spend"].strip() if current.get("actual_spend") else ""
        note = current.get("notes", "").strip()
        
        # Determine actual spend float
        if actual_str == "":
            actual_val = None
        else:
            try:
                actual_val = float(actual_str)
            except ValueError:
                actual_val = None
                
        growth_result = "n/a"
        if actual_val is None:
            # Must be flagged — not computed
            growth_result = f"NULL. Flagged — not computed (Reason: {note})"
            actual_display = "NULL"
        elif i == 0:
            growth_result = "Base period (No previous data)"
            actual_display = f"{actual_val}"
        else:
            prev_str = filtered[i-1]["actual_spend"].strip() if filtered[i-1].get("actual_spend") else ""
            if prev_str == "":
                prev_val = None
            else:
                try:
                    prev_val = float(prev_str)
                except ValueError:
                    prev_val = None
            
            if prev_val is None:
                growth_result = "Cannot compute: previous period null"
            elif prev_val == 0:
                growth_result = "Cannot compute: division by zero"
            else:
                pct = ((actual_val - prev_val) / prev_val) * 100
                sign = "+" if pct > 0 else ""
                
                # Formula presentation: +33.1% [Formula...] (reason) -> using notes if any
                base_formula = f"({actual_val} - {prev_val}) / {prev_val}"
                note_str = f" ({note})" if note else ""
                growth_result = f"{sign}{pct:.1f}% [Formula: {base_formula}]{note_str}"
            
            actual_display = f"{actual_val}"
            
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual_display,
            f"{growth_type} Growth": growth_result
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=True, help="Type of growth to compute (e.g. MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV table")
    
    args = parser.parse_args()
    
    # 1. Load Dataset
    dataset = load_dataset(args.input)
    
    # 2. Compute Growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # 3. Write Output
    if results:
        fieldnames = results[0].keys()
        try:
            with open(args.output, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully computed growth data for '{args.ward}' - '{args.category}'. Output saved to '{args.output}'.")
        except Exception as e:
            print(f"Error writing to {args.output}: {e}")
            sys.exit(1)
    else:
        print("No results to write. Check filters.")

if __name__ == "__main__":
    main()
