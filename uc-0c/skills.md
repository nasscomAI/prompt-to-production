# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates expected columns, reports the count and identity of null actual_spend rows before returning the data.
    input: file_path (str) pointing to ward_budget.csv.
    output: A list of dicts (one per row) with columns period, ward, category, budgeted_amount, actual_spend, notes. Prints a null report listing each null row (period, ward, category, notes) before returning.
    error_handling: If the file is missing or any expected column is absent, raise an error identifying the problem and halt. Never silently drop or fill null actual_spend values — report them explicitly.

  - name: compute_growth
    description: Takes a filtered slice (single ward + single category) and a growth type, and returns a per-period table with the growth value and the formula used for each row.
    input: rows (list of dicts filtered to one ward and one category), growth_type (str — must be exactly 'MoM' or 'YoY'), ward (str), category (str).
    output: A list of dicts with columns period, actual_spend, growth_value, formula, flag. Null rows have growth_value blank and flag set to 'NULL — not computed' with null reason from notes column.
    error_handling: If growth_type is not 'MoM' or 'YoY', raise a ValueError and refuse to compute — do not guess. If the input rows span more than one ward or category, raise a ValueError and refuse — do not aggregate.
