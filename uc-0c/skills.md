# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and reports null count/rows before returning.
    input: Path to ward_budget.csv.
    output: Data collection with null report.
    error_handling: Error if required columns (actual_spend, notes) are missing.

  - name: compute_growth
    description: Computes growth for a ward + category cluster using specified growth type.
    input: Ward string, category string, growth type (MoM/YoY).
    output: Growth table with formula strings.
    error_handling: Returns placeholders for null periods citing the null reason.

