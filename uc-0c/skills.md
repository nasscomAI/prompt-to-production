# skills.md — UC-0C Municipal Budget Growth Analysis Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates column schema, identifies and reports null rows and their reasons before downstream computation.
    input: File path `input_path` (str) pointing to ward_budget.csv.
    output: Tuple containing (rows list, null_report list).
    error_handling: Flags missing columns or file access errors, halting execution before computation.

  - name: compute_growth
    description: Computes period-over-period growth rates for a single ward and category, generating a tabular output with explicit formulas and null flags.
    input: Filtered rows for specific ward, category, and specified growth_type ('MoM' or 'YoY').
    output: Data structure formatted for growth_output.csv with period, ward, category, actual_spend, growth_pct, formula, and notes.
    error_handling: Refuses all-ward or all-category aggregations or missing growth_type, outputting explicit refusal error messages.
