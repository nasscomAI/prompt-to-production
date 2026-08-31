skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates schema and column types, and reports null spend counts and affected rows before returning data.
    input: File path (string) to ward_budget.csv.
    output: Tuple or structured dictionary containing list of validated row records and list of flagged null records with reasons from the notes column.
    error_handling: Raises FileNotFoundError if CSV missing; raises ValueError if required columns are absent or dataset is empty.

  - name: compute_growth
    description: Takes target ward, category, and growth_type, computes period-over-period growth for valid records, and formats output with formula citations and null flags.
    input: Validated dataset records, ward string, category string, and growth_type string (e.g., MoM).
    output: List of formatted dictionary rows containing period, ward, category, actual_spend, growth, formula, and status notes.
    error_handling: Refuses calculation if growth_type is missing/invalid or if cross-ward aggregation is requested.