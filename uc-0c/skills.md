# skills.md

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates that all required columns exist, and reports which rows contain null actual_spend values before returning the data.
    input: A file path (string) pointing to a CSV file with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: A list of dictionaries representing the CSV rows, plus a null_report listing each null row's period, ward, category, and the reason from the notes column. The null_report is printed to stdout before any computation begins.
    error_handling: If the file path is missing or the file does not exist, return "Error: File not found at [path]." If required columns are missing, return "Error: CSV is missing required columns: [list]." If the file is empty, return "Error: CSV file is empty."

  - name: compute_growth
    description: Takes a single ward, category, and growth_type, filters the dataset to that scope, computes period-over-period growth for actual_spend, and returns a per-period table with the formula shown in each row.
    input: (ward: string, category: string, growth_type: string — must be "MoM", dataset: list of row dictionaries from load_dataset).
    output: A list of dictionaries, one per period, each containing: period, actual_spend, previous_period_spend, growth_percentage, formula_used, null_flag (empty string if not null, or the reason from notes if null). Null rows are included but growth fields are left blank with null_flag set.
    error_handling: If the ward or category is not found in the dataset, return "Error: Ward '[ward]' or category '[category]' not found in data." If growth_type is not one of the allowed values (e.g. MoM), return "Error: Unsupported growth type '[type]'. Supported: MoM." If no valid data remains after filtering, return "Error: No data found for the specified ward and category."
