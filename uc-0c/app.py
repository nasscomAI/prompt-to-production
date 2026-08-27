import argparse
import csv
import os
import re

class BudgetAgent:
    def __init__(self, agent_md_path):
        self.role = ""
        self.enforcement_rules = []
        self.load_config(agent_md_path)

    def load_config(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
                self.enforcement_rules = re.findall(r'- "(Rule \d:.*?)"', content)
                role_match = re.search(r'role: >\n\s+(.*?)\n\n', content, re.DOTALL)
                if role_match:
                    self.role = role_match.group(1).strip()
        print(f"[*] Agent Loaded: {self.role}")

    def load_dataset(self, file_path):
        """Skill: load_dataset"""
        data = []
        null_rows = []
        if not os.path.exists(file_path):
            return data, null_rows

        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row['actual_spend'] or row['actual_spend'].strip() == "":
                    null_rows.append(row)
                data.append(row)
        
        print(f"[*] Skill Executed: load_dataset. Found {len(null_rows)} null records.")
        return data, null_rows

    def compute_growth(self, data, ward, category, growth_type):
        """Skill: compute_growth"""
        print(f"[*] Skill Executed: compute_growth (Type: {growth_type})")
        
        # Filter data
        filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
        filtered.sort(key=lambda x: x['period'])
        
        results = []
        for i in range(len(filtered)):
            current = filtered[i]
            res = {
                "period": current['period'],
                "actual_spend": current['actual_spend'],
                "growth": "n/a",
                "formula": "First period - no baseline"
            }
            
            # Check for NULL in current row
            if not current['actual_spend']:
                res["growth"] = "NULL"
                res["formula"] = f"Calculation blocked: {current['notes']}"
                results.append(res)
                continue

            if i > 0 and growth_type == "MoM":
                prev = filtered[i-1]
                if prev['actual_spend']:
                    curr_val = float(current['actual_spend'])
                    prev_val = float(prev['actual_spend'])
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    res["growth"] = f"{growth:+.1f}%"
                    res["formula"] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                else:
                    res["growth"] = "DATA_INCOMPLETE"
                    res["formula"] = f"Previous period ({prev['period']}) was NULL: {prev['notes']}"
            
            results.append(res)
        return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", help="MoM or YoY")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    agent = BudgetAgent(os.path.join(base_dir, "agents.md"))

    # Rule 4: Refuse if growth-type is missing
    if not args.growth_type:
        print("ERROR [Rule 4]: --growth-type is missing. I refuse to guess between MoM or YoY.")
        return

    # Skill 1: Load
    data, nulls = agent.load_dataset(args.input)

    # Rule 2: Report nulls found
    if nulls:
        print("[!] Dataset contains null entries that will affect calculations.")

    # Skill 2: Compute
    results = agent.compute_growth(data, args.ward, args.category, args.growth_type)

    # Save output
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[+] Success! Results written to {args.output}")

if __name__ == "__main__":
    main()
