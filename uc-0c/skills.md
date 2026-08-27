skills:
  - name: load_dataset
      description: Reads the ward budget CSV, validates its columns, and prints a null report for every missing actual_spend value before returning the full dataset.
      input: A file path string pointing to a CSV with columns period, ward, category, budgeted_amount, actual_spend, notes.
      output: A pandas DataFrame containing all 300 rows unmodified — no rows dropped, no values filled.
      error_handling: Exits with [ERROR] and a non-zero code if the file is not found, if any of the 6 required columns are missing, or if the file cannot be parsed as CSV. Null actual_spend values are not errors — they are reported in the NULL REPORT and passed through as-is.

  - name: compute_growth
      description: Computes period-by-period MoM or YoY growth for a single ward + category combination, returning a formula string alongside every result.
      input: A pandas DataFrame (from load_dataset), a ward name string, a category name string, and a growth_type string — either "MoM" or "YoY".
      output: A pandas DataFrame with one row per period and columns period, ward, category, actual_spend_lakh, growth, formula, null_reason. Numeric growth rows carry a full arithmetic formula string, e.g. "(19.7 − 13.2) / 13.2 × 100 = +49.2%". Null or uncomputable rows carry "NOT COMPUTED — <reason>" in growth and "N/A" in formula.
      error_handling: Exits with [ERROR] if the ward + category combination returns zero rows. Sets growth = "NOT COMPUTED — null actual_spend" if the current row is null; "NOT COMPUTED — prior month is null" if the preceding row is null; "NOT COMPUTED — prior month spend is zero (division by zero)" if the denominator is zero. Exits with [ERROR] if growth_type is anything other than "MoM" or "YoY".