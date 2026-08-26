# skills.md

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the expected columns are present, and reports the total null-actual_spend count and which rows (period/ward/category/reason) before any computation happens.
    input: input_path (path to ward_budget.csv).
    output: A list of row dicts (period, ward, category, budgeted_amount, actual_spend, notes) plus a printed/returned null report (count + list of period/ward/category/reason for every row with blank actual_spend).
    error_handling: If a required column is missing from the header, raises a clear error rather than proceeding with a partial schema. Malformed rows are reported, not silently dropped.

  - name: compute_growth
    description: Takes ward + category + growth_type, filters load_dataset's rows to that exact ward/category, and returns a per-period table with the formula shown for every row.
    input: rows (from load_dataset), ward (exact string), category (exact string), growth_type (must be "MoM"; "YoY" is refused — see error_handling).
    output: An ordered list of per-period dicts: period, budgeted_amount, actual_spend, formula, growth_pct — growth_pct is "" with a reason when not computable (null input or no prior period).
    error_handling: Refuses (raises/returns an explicit refusal, does not guess) when — growth_type is missing, growth_type is "YoY" (dataset has only one year, no prior-year baseline exists), ward or category doesn't match any row, or ward/category is an aggregation request ("All"/blank). A null actual_spend in the series produces a NOT COMPUTED row citing the notes-column reason, never a silently skipped or interpolated value.
