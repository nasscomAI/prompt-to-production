# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns are present, and reports the count and identity of null actual_spend rows before returning the data.
    input: Path to the budget CSV file (str).
    output: Tuple of (DataFrame of all rows, list of null-row dicts each containing period, ward, category, and notes). Null rows are reported but kept in the DataFrame so downstream skills can filter them explicitly.
    error_handling: If the file is missing, raise FileNotFoundError with the path. If any required column (period, ward, category, budgeted_amount, actual_spend, notes) is absent, raise ValueError naming the missing column. If the file is empty or has no data rows, raise ValueError stating no data was found.

  - name: compute_growth
    description: Takes a loaded DataFrame, a target ward, a target category, and a growth type (MoM or YoY), and returns a per-period table with the growth formula and result shown for each non-null row.
    input: DataFrame (from load_dataset), ward (str), category (str), growth_type (str — must be exactly "MoM" or "YoY").
    output: List of dicts, one per period, each containing period, actual_spend, formula (str showing the arithmetic), growth_pct (float or None), and flagged (bool). Null actual_spend rows have flagged=True, growth_pct=None, and formula="NULL — not computed".
    error_handling: If growth_type is not "MoM" or "YoY", raise ValueError and instruct the caller to specify one explicitly — do not default. If no rows match the given ward and category, raise ValueError naming the ward and category. Never aggregate across multiple wards or categories; raise ValueError if the filter produces rows spanning more than one ward-category combination.
