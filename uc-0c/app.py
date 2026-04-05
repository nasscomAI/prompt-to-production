"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import pandas as pd
import os

def run_audit():
    input_file = "data/budget/ward_budget.csv"
    output_file = "uc-0c/growth_output.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Skill: budget_loader
    df = pd.read_csv(input_file)

    # Skill: variance_calculator (The "Vibe" Logic)
    # Calculation: (Spent / Allocated) * 100
    df['Utilization_Rate'] = (df['Spent'] / df['Allocated']) * 100
    
    # Enforcement Rules
    def assign_status(row):
        if row['Allocated'] == 0 and row['Spent'] > 0:
            return "CRITICAL_UNAUTHORIZED"
        if row['Utilization_Rate'] > 100:
            return "OVER_BUDGET"
        if row['Utilization_Rate'] < 50:
            return "UNDER_UTILIZED"
        return "HEALTHY"

    df['Status'] = df.apply(assign_status, axis=1)

    # Skill: auditor_reporter
    df.to_csv(output_file, index=False)
    print(f"Audit Complete. Results saved to {output_file}")

if __name__ == "__main__":
    run_audit()