# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning
    input: input_file — path to CSV file
    output: data — list of dicts; null_report — dict with count and row identifiers
    error_handling: raises ValueError if columns missing or file not found

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown
    input: ward — string; category — string; growth_type — "MoM" or "YoY"; data — list of dicts from load_dataset
    output: rows — list of dicts with period, actual_spend, growth, formula, null_flag
    error_handling: raises ValueError if growth_type not supported or ward/category not found

UC-0C Fix [dataset loading]: null rows were silently ignored or aggregated → implemented load_dataset() to validate columns, count nulls (5 rows) and report row identifiers before returning data
UC-0C Fix [growth computation]: silent null handling and unchecked formula → implemented compute_growth() with MoM growth per period, null_flag on every row, and refusal of across-wards/categories aggregation
UC-0C Fix [aggregation refusal]: naive prompts could return single aggregated number → added ward/category filtering and cross-validation that raises ValueError if multiple wards/categories detected
