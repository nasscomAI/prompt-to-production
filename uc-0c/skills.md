skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns are present, and reports the count and details of all null actual_spend rows before returning the full dataset.
    input: file_path (string, path to ward_budget.csv)
    output: dict with keys data (list of row dicts), null_rows (list of dicts with period, ward, category, notes for each null actual_spend row), total_rows (int)
    error_handling: If the file is not found, raise FileNotFoundError with the path. If required columns (period, ward, category, actual_spend, notes) are missing, raise ValueError listing the missing column names. Never return data without first reporting null row count and details.

  - name: compute_growth
    description: Filters the dataset to the specified ward and category, then returns a per-period table with actual_spend, previous_spend, formula, and computed growth percentage for each period.
    input: dataset (dict as returned by load_dataset), ward (string, exact match), category (string, exact match), growth_type (string, must be exactly MoM or YoY)
    output: list of dicts each with keys period, ward, category, actual_spend, previous_spend, formula, growth_pct, flag; one dict per period in the filtered dataset
    error_handling: If growth_type is not exactly MoM or YoY, raise ValueError and refuse to guess — do not default. If no rows match the ward and category, raise ValueError with a clear message. When either current or previous actual_spend is null, set growth_pct to null and flag to the null reason — never compute growth from a null value.
