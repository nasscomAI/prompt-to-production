"""
UC-0C app.py — Starter file.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                raise ValueError("Empty dataset")
                
            required = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            for req in required:
                if req not in headers:
                    raise ValueError(f"Missing required column: {req}")
            
            data = list(reader)
            
            null_count = 0
            null_details = []
            for idx, row in enumerate(data):
                if not row['actual_spend'].strip():
                    null_count += 1
                    # Extract identically to requirements logic in agents.md
                    null_details.append(f"Row {idx+2} ({row['period']}, {row['ward']}, {row['category']}) flagged null. Reason: '{row['notes']}'")
                    
            if null_count > 0:
                print(f"DIAGNOSTIC REPORT: Found {null_count} null entries in actual_spend.")
                for detail in null_details:
                    print(f"FLAG: {detail}")
                    
            return data
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Provided dataset {input_path} could not be located.")


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Implements Refusal condition securely.
    """
    # 1. Refusal on broad aggregation
    if not ward or not category:
        raise ValueError("REFUSAL: Cannot aggregate across wards or categories organically. Explicit granular specification is mandatory.")
        
    # 2. Refusal on assumed methodology
    if not growth_type:
        raise ValueError("REFUSAL: Growth methodology (--growth-type) is withheld. Refusing to guess between variants like MoM or YoY.")
        
    if growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError(f"REFUSAL: Unknown growth variant '{growth_type}'. Only 'MoM' or 'YoY' supported.")

    # 3. Filtering specific constraints
    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    # Mathematical logic implementation displaying formulas identically to agents.md intent constraints
    if growth_type.upper() == "MOM":
        for i in range(len(filtered)):
            current = filtered[i]
            cur_spend_str = current['actual_spend'].strip()
            
            out_row = {
                "period": current["period"],
                "ward": current["ward"],
                "category": current["category"],
                "actual_spend": cur_spend_str if cur_spend_str else "NULL",
                "notes": current["notes"],
                "growth": "",
                "formula": ""
            }
            
            if not cur_spend_str:
                out_row["growth"] = "FLAG: NULL (Computation refused)"
                out_row["formula"] = "N/A - Missing current month actuals"
                results.append(out_row)
                continue
                
            cur_spend = float(cur_spend_str)
            
            if i == 0:
                out_row["growth"] = "Baseline"
                out_row["formula"] = "N/A - Start Period"
                results.append(out_row)
                continue
                
            prev = filtered[i-1]
            prev_spend_str = prev['actual_spend'].strip()
            
            if not prev_spend_str:
                out_row["growth"] = "FLAG: Previous month NULL (Computation refused)"
                out_row["formula"] = "N/A - Missing prior month actuals"
                results.append(out_row)
                continue
                
            prev_spend = float(prev_spend_str)
            
            if prev_spend == 0:
                out_row["growth"] = "undefined"
                out_row["formula"] = f"({cur_spend} - 0) / 0"
            else:
                growth_pct = ((cur_spend - prev_spend) / prev_spend) * 100
                out_row["growth"] = f"{growth_pct:+.1f}%"
                out_row["formula"] = f"(({cur_spend} - {prev_spend}) / {prev_spend}) * 100"
                
            results.append(out_row)

    elif growth_type.upper() == "YOY":
        raise ValueError("REFUSAL: YoY calculation requires multi-year dataset spanning identical subsequent months.")
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input CSV dataset")
    parser.add_argument("--output", required=True, help="Path to write output CSV dataset")
    parser.add_argument("--ward", default=None, help="Explicit ward targeted to prevent silent aggregations")
    parser.add_argument("--category", default=None, help="Explicit category targeted to prevent silent aggregations")
    parser.add_argument("--growth-type", dest="growth_type", default=None, help="Explicit computation variant (MoM/YoY)")
    
    args = parser.parse_args()
    
    try:
        dataset = load_dataset(args.input)
        computed = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            headers = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(computed)
            
        print(f"Done. Results written to {args.output}")
        
    except ValueError as ve:
        # Halt execution rather than silently failing or guessing 
        print(f"\n{ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
