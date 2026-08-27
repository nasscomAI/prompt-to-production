skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns are present, reports null count and which specific rows are null before returning the data.
    input: Absolute or relative file path to ward_budget.csv.
    output: A list of row dictionaries, preceded by a printed null report listing each null row's period, ward, category, and notes value.
    error_handling: If the file is missing, raise FileNotFoundError. If required columns (period, ward, category, actual_spend, notes) are absent, raise ValueError listing the missing columns. Always report nulls before returning data — never silently skip them.

  - name: compute_growth
    description: Takes a filtered dataset for a specific ward and category, computes MoM or YoY growth per period, and returns a per-period table with the formula shown alongside each result.
    input: List of row dicts (filtered to one ward + one category), and growth_type string ("MoM" or "YoY").
    output: A list of result dicts containing period, ward, category, actual_spend, growth_pct, formula, and flag (NULL_FLAG or empty string).
    error_handling: If growth_type is not "MoM" or "YoY", raise ValueError with the message "Please specify --growth-type as MoM or YoY. This system will not guess." If actual_spend is null for a row, output NULL_FLAG with the reason from the notes column and skip computing growth for that row. If the previous period's actual_spend is also null, output NULL_FLAG on the current row as well since the formula cannot be computed.
