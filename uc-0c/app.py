"""
UC-0C app.py — Financial Analytics
Implemented utilizing agents.md and skills.md RICE frameworks.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """
    Safely reads the CSV, logs exact locations of missing values, returns structured rows.
    """
    rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            missing_count = 0
            for i, row in enumerate(reader, start=1):
                if not row.get('actual_spend') or row['actual_spend'].strip() == '':
                    missing_count += 1
                    print(f"NULL FLAG: Row {i} | Ward: {row['ward']} | Category: {row['category']} | Reason: {row.get('notes')}")
                rows.append(row)
            print(f"Dataset loaded. Identified {missing_count} explicit null records.")
            return rows
    except Exception as e:
        sys.exit(f"System Error: Failed to load dataset {filepath} — {e}")

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes rigorous per-category, per-ward analytics without silent aggregation.
    """
    # Strict Configuration Constraints Enforcements
    if not ward or ward.lower() == 'all':
        sys.exit("Refused: Never aggregate across wards unless explicitly instructed.")
    if not category or category.lower() == 'all':
        sys.exit("Refused: Never aggregate across categories unless explicitly instructed.")
    if not growth_type:
        sys.exit("Refused: --growth-type must be explicitly specified (e.g., MoM, YoY). Never guessing parameters.")
        
    if growth_type.upper() not in ["MOM", "YOY"]:
        sys.exit(f"Refused: Unknown growth_type '{growth_type}'. Only MoM/YoY supported.")
        
    # Dataset parsing rigidly on constrained target
    subset = [r for r in rows if r['ward'] == ward and r['category'] == category]
    subset.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(subset):
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row.get('notes', '').strip()
        note_str = f" ({notes})" if notes else ""
        
        # Rule 2: Nulls flagged, rule 3: Formulas printed
        if not actual_spend:
            growth_result = f"Must be flagged — not computed{note_str}"
            results.append((ward, category, period, "NULL", growth_result))
            continue
            
        current_val = float(actual_spend)
        
        prev_val = None
        if growth_type.upper() == "MOM" and i >= 1:
            prev_spend = subset[i-1]['actual_spend']
            if prev_spend:
                prev_val = float(prev_spend)
        elif growth_type.upper() == "YOY" and i >= 12:
            prev_spend = subset[i-12]['actual_spend']
            if prev_spend:
                prev_val = float(prev_spend)
                
        if prev_val is None:
            growth_result = "n/a (no prior period)"
        else:
            growth_pct = ((current_val - prev_val) / prev_val) * 100
            sign = "+" if growth_pct > 0 else ""
            formula = f"[Formula: ({current_val} - {prev_val}) / {prev_val} = {growth_pct:.1f}%]"
            growth_result = f"{sign}{growth_pct:.1f}% {formula}{note_str}"
            
        results.append((ward, category, period, current_val, growth_result))
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Analytics")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False, default=None)
    parser.add_argument("--category", required=False, default=None)
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Grid construction explicitly tracking formula
    try:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Ward", "Category", "Period", "Actual Spend (lakh)", f"{args.growth_type} Growth"])
            writer.writerows(results)
        print(f"Done. Per-ward output generated safely at {args.output}")
    except Exception as e:
        sys.exit(f"Failed to write output file: {e}")

if __name__ == "__main__":
    main()
