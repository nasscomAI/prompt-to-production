import argparse
import csv

def load_dataset(input_path: str):
    """reads CSV, validates columns, reports null count and which rows before returning"""
    data = []
    nulls = 0
    with open(input_path, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            if not row.get("actual_spend") or row.get("actual_spend").strip().lower() in ['null', '']:
                nulls += 1
                
    if nulls > 0:
        print(f"Dataset loaded. Flagged {nulls} null rows.")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """takes ward + category + growth_type, returns per-period table with formula shown"""
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified — refuse and ask, never guess")
    if not ward or not category or ward.lower() == "any" or category.lower() == "any":
        raise ValueError("REFUSAL: Never aggregate across wards or categories unless explicitly instructed.")
        
    filtered = []
    for row in data:
        if row.get("ward") == ward and row.get("category") == category:
            filtered.append(row)
            
    filtered.sort(key=lambda x: x.get("period", ""))
    
    results = []
    if growth_type.upper() == "MOM":
        for i in range(len(filtered)):
            current_row = filtered[i]
            period = current_row.get("period", "")
            actual_str = current_row.get("actual_spend", "").strip().lower()
            
            if actual_str in ["", "null"]:
                reason = current_row.get("notes", "Unknown reason")
                results.append({
                    "Ward": ward,
                    "Category": category,
                    "Period": period,
                    "Actual Spend (Lakhs)": "NULL",
                    "Growth": f"Must be flagged — not computed ({reason})",
                    "Formula": "N/A"
                })
                continue
                
            actual = float(current_row.get("actual_spend", 0))
            if i == 0:
                results.append({
                    "Ward": ward,
                    "Category": category,
                    "Period": period,
                    "Actual Spend (Lakhs)": actual,
                    "Growth": "N/A",
                    "Formula": "Base Month"
                })
                continue
                
            prev_str = filtered[i-1].get("actual_spend", "").strip().lower()
            if prev_str in ["", "null"]:
                results.append({
                    "Ward": ward,
                    "Category": category,
                    "Period": period,
                    "Actual Spend (Lakhs)": actual,
                    "Growth": "N/A",
                    "Formula": "Previous month was NULL"
                })
                continue
                
            prev_actual = float(filtered[i-1].get("actual_spend", 0))
            growth = ((actual - prev_actual) / prev_actual) * 100 if prev_actual else 0
            
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": actual,
                "Growth": f"{growth:+.1f}%",
                "Formula": f"({actual} - {prev_actual}) / {prev_actual} * 100"
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False, default=None)
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        if results:
            keys = results[0].keys()
            with open(args.output, "w", encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Outputs written to {args.output}")
    except ValueError as e:
        print(e)
        
if __name__ == "__main__":
    main()
