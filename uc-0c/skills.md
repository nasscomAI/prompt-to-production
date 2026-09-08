skills:
  - name: load_dataset
    description: Reads the municipal budget CSV file, validates required schema columns, performs a pre-computation null audit, and reports all missing value rows and reasons.
    input: Filepath string to the budget CSV file (e.g., ward_budget.csv).
    output: Structured dataset of validated records along with a detailed list of detected null rows and notes.
    error_handling: Raises FileNotFoundError if path is invalid; raises ValueError if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or corrupted.

  - name: compute_growth
    description: Computes period-by-period budget expenditure growth for an isolated ward and category under a specified formula type (e.g., MoM), showing exact formulas and handling null periods safely.
    input: Validated dataset, ward name string, category name string, and growth_type string ('MoM' or 'YoY').
    output: List of structured output records containing period, ward, category, budgeted_amount, actual_spend, growth_rate_pct, formula_used, and status/notes.
    error_handling: Refuses execution if ward or category is missing or requests cross-ward aggregation; refuses if growth_type is unspecified; outputs explicit null status when computing across missing periods.
