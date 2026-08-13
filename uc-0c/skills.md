# skills.md

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns, reports null count and specific null rows before returning data.
    input: File path to CSV string.
    output: pandas DataFrame plus a null_report dict listing null rows with their notes.
    error_handling: If file missing or columns invalid, raise error with clear message.

  - name: compute_growth
    description: Takes filtered DataFrame for one ward + one category + growth type, computes period-over-period growth with formula shown.
    input: DataFrame, ward name string, category name string, growth_type string (MoM or YoY).
    output: DataFrame with columns period, actual_spend, prev_value, growth_pct, formula, null_flag.
    error_handling: If growth_type unsupported, refuse. If insufficient data, return empty with explanation.