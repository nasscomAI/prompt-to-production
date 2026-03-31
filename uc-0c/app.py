import argparse
import csv
import sys

def load_dataset(input_path: str):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames if reader.fieldnames else [])
        if not required_cols.issubset(headers):
            raise ValueError(f"Missing required columns in CSV. Expected {required_cols}")
            
        for i, row in enumerate(reader, start=2):
            item = dict(row)
            if not item.get("actual_spend") or item["actual_spend"].strip() == "":
                null_rows.append({
                    "row_num": i,
                    "period": item.get("period", ""),
                    "ward": item.get("ward", ""),
                    "category": item.get("category", ""),
                    "reason": item.get("notes", "")
                })
            data.append(item)
            
    print(f"--- DATASET REPORT ---")
    print(f"Total rows loaded: {len(data)}")
    print(f"Total null actual_spend values explicitly detected: {len(null_rows)}")
    for nr in null_rows:
        print(f"  - Row {nr['row_num']} [{nr['period']} · {nr['ward']} · {nr['category']}] -> Null Reason: {nr['reason']}")
    print("-" * 22)
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Enforces RICE rules from agents.md.
    """
    if not ward or ward.lower() == "all":
        raise ValueError("REFUSAL: Never aggregate across wards unless explicitly instructed. Please specify a single ward.")
    if not category or category.lower() == "all":
        raise ValueError("REFUSAL: Never aggregate across categories unless explicitly instructed. Please specify a single category.")
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified. Cannot guess the growth formula.")
        
    if growth_type.upper() != "MOM":
        raise ValueError(f"REFUSAL: Unsupported growth_type '{growth_type}'. This agent currently only computes MoM.")

    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    filtered.sort(key=lambda x: x["period"])
    
    output_rows = []
    for i in range(len(filtered)):
        current = filtered[i]
        period = current["period"]
        actual_spend_str = current.get("actual_spend", "").strip()
        
        if not actual_spend_str:
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": "NULL",
                "Growth": "FLAGGED",
                "Formula": f"NULL value in source. Reason: {current.get('notes', 'Unknown')}"
            })
            continue
            
        current_spend = float(actual_spend_str)
        
        if i == 0:
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": current_spend,
                "Growth": "n/a",
                "Formula": "First period in series, no previous data available."
            })
            continue
            
        prev = filtered[i-1]
        prev_spend_str = prev.get("actual_spend", "").strip()
        
        if not prev_spend_str:
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": current_spend,
                "Growth": "FLAGGED",
                "Formula": "Previous period was NULL, cannot compute growth."
            })
            continue
            
        prev_spend = float(prev_spend_str)
        
        if prev_spend == 0:
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": current_spend,
                "Growth": "FLAGGED",
                "Formula": f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100 -> Division by zero."
            })
        else:
            growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
            formula_sign = "+" if growth_pct >= 0 else ""
            notes_str = f" ({current['notes'].strip()})" if current.get('notes') and current['notes'].strip() else ""
            formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            
            output_rows.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": current_spend,
                "Growth": f"{formula_sign}{growth_pct:.1f}%{notes_str}",
                "Formula": formula
            })
            
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=False, help="Specific ward to process")
    parser.add_argument("--category", required=False, help="Specific category to process")
    parser.add_argument("--growth-type", required=False, help="Growth type to compute (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            headers = ["Ward", "Category", "Period", "Actual Spend (Lakhs)", "Growth", "Formula"]
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Results successfully computed and written to {args.output}")
        
    except ValueError as ve:
        if str(ve).startswith("REFUSAL:"):
            print(f"\n[AGENT REFUSAL] → {ve}", file=sys.stderr)
        else:
            print(f"Error: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
