# skills.md

skills:
  - name: "load_dataset"
    description: "Reads the budget CSV, validates columns, and explicitly identifies rows with null Actual Spend before processing."
    input: "Path to ward_budget.csv."
    output: "Valid data object and a summary of null rows identified."
    error_handling: "If the CSV structure is invalid, report columns found vs expected and halt."

  - name: "compute_growth"
    description: "Calculates growth (e.g., MoM) for a filtered dataset, injecting formulas into the output for transparency."
    input: "Filtered data (ward + category) and growth_type (MoM/YoY)."
    output: "CSV/Table with period, actual_spend, growth percentage, and formula suffix."
    error_handling: "If a prior period is missing for a MoM calculation, set growth to 'n/a' and explain the missing comparison point."
