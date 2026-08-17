skills:
  - name: load_dataset
    description: Reads the municipal budget CSV, validates required columns, and identifies/reports null actual spend rows with their notes before returning data.
    input: String file_path (path to input CSV file).
    output: Validated tabular dataset (list of record dictionaries or DataFrame) containing columns (period, ward, category, budgeted_amount, actual_spend, notes) and a null report mapping flagged rows to their reasons.
    error_handling: Raises an error if the input file does not exist, is unreadable, or is missing required columns; explicitly flags any null actual_spend rows using explanations from the notes column rather than silently dropping or imputing values.

  - name: compute_growth
    description: Computes period-over-period spend growth for a specific ward and category, returning a per-period table with explicit formula documentation.
    input: Validated dataset records, string ward, string category, string growth_type (e.g., "MoM", "YoY"), and optional string output_path.
    output: Per-period growth analysis table (and optional destination CSV) containing period, ward, category, budgeted_amount, actual_spend, growth_rate, formula, and notes.
    error_handling: Refuses execution if growth_type is missing/unsupported, if ward or category is not specified, or if requested to aggregate across wards/categories; flags null rows and subsequent affected comparisons as non-computable with explanation notes instead of calculating invalid rates.
