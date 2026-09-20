skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates required columns, and flags missing or null actual_spend rows along with notes.
    input: Filepath string pointing to the input budget CSV file (--input).
    output: Tuple or List of validated row dictionaries, alongside a report of detected null actual_spend rows and their corresponding notes.
    error_handling: If the input file is missing or invalid, raises FileNotFoundError. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raises ValueError. Missing or null actual_spend values are explicitly flagged as NULL_SPEND with reason extracted from notes rather than silently dropped or imputed.

  - name: compute_growth
    description: Calculates period-over-period spend growth for a specific ward and category using the specified growth type formula.
    input: Dataset list from load_dataset, ward string (--ward), category string (--category), and growth_type string (--growth-type).
    output: List of output dictionaries containing period, ward, category, budgeted_amount, actual_spend, mom_growth, formula_used, and notes, suitable for CSV export.
    error_handling: Refuses execution if growth_type is missing, empty, or not supported (e.g., must specify 'MoM' or 'YoY'). Refuses execution if requested to aggregate across all wards or all categories into a single summary number. If actual_spend is null for the current or comparison period, growth calculation is skipped, mom_growth is set to 'NULL', and the note explaining the missing data is included.
