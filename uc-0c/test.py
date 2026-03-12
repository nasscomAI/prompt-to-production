import sys
import csv

def run():
    print("Loading data...")
    data = []
    with open('../data/budget/ward_budget.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            
    print(f"Loaded {len(data)} rows.")
    ward = "Ward 1 – Kasba"
    category = "Roads & Pothole Repair"
    
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x["period"])
    print(f"Filtered to {len(filtered)} rows.")
    
    results = []
    for i in range(len(filtered)):
        curr_row = filtered[i]
        period = curr_row["period"]
        actual_spend = curr_row.get("actual_spend", "").strip()
        notes = curr_row.get("notes", "").strip()
        
        prev_idx = i - 1
        growth_pct = "NULL"
        formula = ""
        flag = ""
        
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
                try:
                    curr_val = float(actual_spend)
                    prev_val = float(prev_spend)
                    if prev_val == 0:
                        formula = f"({curr_val} - 0) / 0"
                        growth_pct = "Inf"
                    else:
                        g = ((curr_val - prev_val) / prev_val) * 100
                        if g > 0:
                            growth_pct = f"+{g:.1f}%"
                        else:
                            growth_pct = f"{g:.1f}%"
                        formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                        flag = notes
                except:
                    pass
        
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend if actual_spend else "NULL",
            "growth_pct": growth_pct,
            "formula": formula,
            "flag": flag
        })
        
    print(f"Computed {len(results)} rows.")
    with open('growth_output.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"])
        writer.writeheader()
        writer.writerows(results)
    print("Done!")

if __name__ == '__main__':
    run()
