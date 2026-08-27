# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads a CSV file, validates required columns exist, and reports null count and which rows have null values before returning the data.
    input: file_path (str) — path to a CSV file with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: A tuple of (data as list of dicts, null_summary as list of dicts). Null summary contains row details with null actual_spend values and their notes.
    error_handling: If file is missing, raise FileNotFoundError. If required columns are missing, raise ValueError listing which columns are missing. If actual_spend has non-numeric values, log the row and continue.

  - name: compute_growth
    description: Takes ward, category, and growth_type parameters, computes per-period growth, and returns a table with formula shown for every row.
    input: data (list of dicts), ward (str), category (str), growth_type (str) — either "MoM" or "YoY".
    output: A list of dicts with keys: period (str), actual_spend (float or "NULL"), growth_pct (float or "FLAGGED"), formula (str). Null rows show "FLAGGED" and the null reason from notes.
    error_handling: If ward or category not found in data, raise ValueError. If growth_type is not MoM or YoY, raise ValueError. If a period has no previous period for MoM, show "N/A" for that row's growth.
