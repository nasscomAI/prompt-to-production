skills:
  - name: load_dataset
    description: Reads a municipal ward budget CSV file, validates required schema and columns, scans for missing actual spend records, and reports null count and row-level null details before returning validated records.
    input: file_path (str, path to the input CSV file containing columns: period, ward, category, budgeted_amount, actual_spend, notes).
    output: Dict[str, Any] containing 'records' (List[Dict[str, Any]] with typed rows: period, ward, category, budgeted_amount, actual_spend, notes), 'null_records' (List[Dict[str, Any]] detailing every row where actual_spend is null or empty, with reason from notes), and 'total_rows' (int).
    error_handling: If the input file does not exist, cannot be read, is empty, or lacks any of the required columns (period, ward, category, budgeted_amount, actual_spend, notes), raises FileNotFoundError or ValueError with a descriptive refusal message.

  - name: compute_growth
    description: Filters validated budget records by specified ward and category, verifies valid growth metric, and computes period-over-period spend growth while explicitly documenting the formula applied and flagging null periods without computing synthetic values.
    input: records (List[Dict[str, Any]], validated budget records from load_dataset), ward (str, target ward name), category (str, target budget category name), growth_type (str, growth calculation type, e.g. 'MoM' or 'YoY').
    output: List[Dict[str, Any]] representing a per-period table where each row contains period, ward, category, budgeted_amount, actual_spend, growth_type, growth_pct (Optional[float] or formatted str, e.g., '+33.1%', or 'NULL'), formula (str, showing exact mathematical expression used), and notes (str, explaining null or special conditions).
    error_handling: If growth_type is missing or not supported (e.g. neither 'MoM' nor 'YoY'), refuses execution with ValueError; if ward or category is not specified or set to aggregate all wards/categories, refuses execution to prevent wrong aggregation; if ward or category is not found in the dataset, raises ValueError; if actual_spend is null for the current or comparison period, marks growth as uncomputable, records the reason from notes, and does not compute.
