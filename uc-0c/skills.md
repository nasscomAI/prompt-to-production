# skills.md — UC-0C Budget Growth Analyser

skills:
  - name: load_dataset
    description: Read the budget CSV, validate columns, and report all NULL rows before any computation.
    input: input_path to ward_budget.csv.
    output: >
      (rows, null_rows) — rows is the full list of dict records; null_rows lists
      every record whose actual_spend is blank. Prints each NULL row's period,
      ward, category and notes reason to stdout before returning.
    error_handling: >
      If required columns are missing, refuses (exit 2) with a clear message.
      NULLs are reported, never silently dropped or zero-filled.

  - name: compute_growth
    description: Compute per-period MoM/YoY growth for one ward + one category, flagging NULLs.
    input: rows, ward (single), category (single), growth_type ∈ {MoM, YoY}.
    output: >
      A list of dicts (one per period) with period, ward, category, actual_spend,
      growth_percentage, formula_applied, null_flag_reason. growth_percentage is
      rounded to 1 decimal or 'n/a' when not computable.
    error_handling: >
      Refuses all-ward / all-category requests and unknown ward/category combos.
      Sets growth_percentage = n/a (with a reason) when the current or prior
      period is NULL, when there is no prior period, or when the prior value is 0.
