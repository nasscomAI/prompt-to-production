skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates required columns exist, reports
      total row count, count of null actual_spend rows, and lists which rows
      (period + ward + category) are null along with their notes.
    input: >
      file path (string) — path to a CSV with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A tuple of (pandas DataFrame, list of null-row dicts). Each null-row
      dict has keys: period, ward, category, notes.
    error_handling: >
      If file not found → raise FileNotFoundError with path. If any required
      column is missing → raise ValueError listing missing columns. If
      actual_spend cannot be parsed as float → warn and treat as null.

  - name: compute_growth
    description: >
      Given a filtered DataFrame, ward name, category name, and growth type
      (MoM or YoY), returns a per-period table with previous period's spend,
      growth percentage, the formula string, and any null-flags.
      Supports MoM (period-1 month) and YoY (period-12 months).
    input: >
      df (DataFrame) — pre-filtered to a single ward + category; ward (str);
      category (str); growth_type (str, "MoM" or "YoY").
    output: >
      DataFrame with columns: period, ward, category, actual_spend,
      previous_spend, growth_pct, formula, note. Rows with null actual_spend
      or null previous_spend have growth_pct = "NULL".
    error_handling: >
      If growth_type not in ("MoM", "YoY") → raise ValueError. If DataFrame
      is empty → return empty DataFrame. If only one period exists and
      growth_type = "MoM" → all growth_pct = "NULL" (no prior period).
