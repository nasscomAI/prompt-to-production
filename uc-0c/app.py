"""
UC-0C app.py — Number That Looks Right
Implements load_dataset and compute_growth per constraint rules:
1. No aggregation across wards/categories
2. Explicitly flag nulls and report reasoning
3. Force formula transparency
4. Refuse calculation if growth_type is missing
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """
    Skill: load_dataset
    Reads CSV, validates, reports nulls before returning.
    """
    data = []
    nulls_detected = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Store original row
                data.append(row)
                
                # Check for explicit nulls
                # "actual_spend" might be empty string or literally "NULL"
                spend_val = row.get("actual_spend", "").strip().upper()
                if not spend_val or spend_val == "NULL":
                    nulls_detected.append({
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "notes": row.get("notes", "No note provided")
                    })
    except Exception as e:
        print(f"[ERROR] Failed to load dataset {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Dataset loaded: {len(data)} rows.")
    if nulls_detected:
        print(f"\n[ALERT] Detected {len(nulls_detected)} null 'actual_spend' records:", file=sys.stderr)
        for n in nulls_detected:
            print(f"  - {n['period']} | {n['ward']} | {n['category']} => Reason: {n['notes']}", file=sys.stderr)
        print("", file=sys.stderr)
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: compute_growth
    Refuses cross-aggregation. Computes period-over-period strictly.
    """
    # Enforcement 4: If growth_type not specified — refuse and ask, never guess
    if not growth_type:
        print("[ERROR] Refusal: --growth-type not specified. I cannot guess whether you want MoM, YoY, or another metric. Please specify.", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement 1: Never aggregate across wards or categories
    if not ward or ward.lower() == "any" or ward.lower() == "all":
        print("[ERROR] Refusal: You asked to aggregate across wards. My rules explicitly forbid blind aggregation across entities.", file=sys.stderr)
        sys.exit(1)
        
    if not category or category.lower() == "any" or category.lower() == "all":
        print("[ERROR] Refusal: You asked to aggregate across categories. My rules explicitly forbid blind aggregation.", file=sys.stderr)
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"[ERROR] Only 'MoM' growth is currently supported in this script. Received '{growth_type}'", file=sys.stderr)
        sys.exit(1)

    # Filter data
    filtered = [d for d in data if d["ward"] == ward and d["category"] == category]
    
    if not filtered:
        print(f"[WARN] No data found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        return []

    # Sort strictly by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i, current in enumerate(filtered):
        period = current["period"]
        spend_str = current.get("actual_spend", "").strip().upper()
        
        is_null_current = not spend_str or spend_str == "NULL"
        
        # Output row structure
        out_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": "NULL" if is_null_current else spend_str,
            "MoM Growth": "",
            "Formula Used": "",
            "Flag": "NULL explicitly preserved" if is_null_current else ""
        }
        
        # Compute MoM
        if i == 0:
            out_row["MoM Growth"] = "n/a"
            out_row["Formula Used"] = "First period, no previous period to compare"
            if is_null_current:
                out_row["MoM Growth"] = "Must be flagged — not computed"
                out_row["Formula Used"] = f"Cannot compute: {current.get('notes', 'Missing data')}"
        else:
            prev = filtered[i-1]
            prev_spend_str = prev.get("actual_spend", "").strip().upper()
            is_null_prev = not prev_spend_str or prev_spend_str == "NULL"
            
            if is_null_current or is_null_prev:
                # Enforcement 2: Flag every null row before computing
                out_row["MoM Growth"] = "Must be flagged — not computed"
                reason_cur = current.get("notes", "Missing data")
                reason_prev = prev.get("notes", "Previous period missing")
                
                if is_null_current:
                    out_row["Formula Used"] = f"Cannot compute: Current period missing. Reason: {reason_cur}"
                else: # previous is null
                    out_row["Formula Used"] = f"Cannot compute: Previous period ({prev['period']}) missing. Reason: {reason_prev}"
            else:
                try:
                    v_cur = float(spend_str)
                    v_prev = float(prev_spend_str)
                    
                    if v_prev == 0:
                        out_row["MoM Growth"] = "n/a (Denominator is 0)"
                        out_row["Formula Used"] = f"({v_cur} - 0) / 0"
                    else:
                        growth_pct = ((v_cur - v_prev) / v_prev) * 100
                        # Try to attach notes for anomalies if present, to match the reference value style "(monsoon spike)"
                        note_suffix = f" ({current.get('notes')})" if current.get('notes') else ""
                        out_row["MoM Growth"] = f"{growth_pct:+.1f}%{note_suffix}"
                        out_row["Formula Used"] = f"({v_cur} - {v_prev}) / {v_prev}"
                except ValueError:
                    out_row["MoM Growth"] = "Data Error"
                    out_row["Formula Used"] = "Failed to parse numeric value"

        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    # Optional arguments to allow the "Refuse and Ask" logic from Enforcement 4 & 1
    parser.add_argument("--ward", default="Any", help="Strict constraint for Ward")
    parser.add_argument("--category", default="Any", help="Strict constraint for Category")
    parser.add_argument("--growth-type", help="Growth metric to calculate (e.g. MoM)")

    args = parser.parse_args()

    # Load and validate
    data = load_dataset(args.input)
    
    # Compute safely
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("[INFO] No output generated due to earlier constraints or missing data.", file=sys.stderr)
        sys.exit(0)
        
    # Write Output
    fields = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth", "Formula Used", "Flag"]
    
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"[ERROR] Failed to write to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Generated {len(results)} rows of explicit per-period logic safely to {args.output}")

if __name__ == "__main__":
    main()
