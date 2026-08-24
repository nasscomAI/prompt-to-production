skills:
  - name: load_dataset
    description: Ingests the ward budget CSV, verifies column schemas, identifies and audits all null actual_spend rows against notes, and indexes rows by ward, category, and period.
    input: File path input_path (str) pointing to ward_budget.csv.
    output: Tuple containing list of row records and a dictionary summary of audited null rows with reasons.
    error_handling: Raises FileNotFoundError if CSV missing; raises ValueError if required columns are absent.

  - name: compute_growth
    description: Filters records for an explicit single ward and category, verifies presence of growth_type, calculates period-over-period percentage growth, flags nulls, and attaches exact formula strings.
    input: Ward (str), category (str), growth_type (str: 'MoM' or 'YoY'), list of filtered rows.
    output: List of structured result rows with period, ward, category, budgeted_amount, actual_spend, mom_growth, formula, and status_flag.
    error_handling: Refuses computation if ward/category spans multiple entities; raises refusal error if growth_type is missing or invalid.
