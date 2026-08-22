skills:
  - name: ward_budget_reader
    description: Reads and sanitizes tabular municipal budget CSV records across fiscal years.
    input: File path to ward_budget.csv.
    output: List of validated dictionary records with numeric budget fields.
    error_handling: Coerces invalid or empty numeric values to float 0.0 and tags records with validation flags.

  - name: granular_growth_calculator
    description: Calculates localized year-over-year expenditure variance and percentage growth per ward-category pair.
    input: Dictionary containing ward_id, category, previous fiscal year budget, and current fiscal year budget.
    output: Computed numerical metrics including absolute change and rounded percentage growth.
    error_handling: Handles zero-division when previous year budget is zero by setting growth to 0.0 and flagging new allocation.

  - name: budget_report_exporter
    description: Writes granular budget growth computations into standard CSV format.
    input: Processed budget rows and destination output path.
    output: CSV file (growth_output.csv).
    error_handling: Creates target directory if nonexistent and replaces corrupted rows with formatted error rows.