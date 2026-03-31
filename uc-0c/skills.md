skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null count with affected row details before returning data.
    input: CSV file path (string).
    output: Parsed dataset (list of dicts) with columns: period, ward, category, budgeted_amount, actual_spend, notes. Also returns null_report listing each null row (period, ward, category, reason).
    error_handling: If file not found, report missing path. If required columns are absent, list the missing columns and refuse to proceed. If null actual_spend rows exist, flag them with their notes before returning — do not silently drop or fill them.

  - name: compute_growth
    description: Takes a ward, category, and growth_type (MoM or YoY), filters the dataset, and returns a per-period growth table with formulas shown.
    input: ward (string), category (string), growth_type (one of "MoM" or "YoY"), dataset (list of dicts from load_dataset).
    output: List of dicts with columns: period, actual_spend, growth_pct, formula (e.g. "(current - previous) / previous * 100"). Rows with null actual_spend are included with growth_pct = NULL and a flag.
    error_handling: If growth_type is not "MoM" or "YoY", refuse and ask the user to specify. If ward or category not found in dataset, report available values and refuse. If no non-null data points exist for the filter, report that growth cannot be computed.
