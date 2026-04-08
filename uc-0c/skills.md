skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates that required columns are present, and reports the count and location of any null actual_spend rows.
    input: String path to the input CSV.
    output: A data frame or list of dictionaries containing the parsed data, and a summary list of any nulls found.
    error_handling: Return descriptive errors if columns are missing or file unreadable.

  - name: compute_growth
    description: Computes per-period growth for a specific ward and category using a specific growth type, appending the mathematical formula to the output row.
    input: The loaded dataset, a specific ward string, a specific category string, and a growth_type string (e.g., MoM).
    output: A formatted CSV output table of the computed per-period metrics and formulas. Flag any null periods without computation.
    error_handling: Refuse execution if ward, category, or growth_type is missing. Refuse if asked to aggregate 'All' without explicit override parameters.
