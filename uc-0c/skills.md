# skills.md — UC-0C Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates column schema, and logs detected null actual_spend rows.
    input: File path (string) to ward_budget.csv.
    output: A list of row dicts with validated types and a list of identified null rows with notes.
    error_handling: Refuses if required columns are missing; explicitly reports all null actual_spend rows.

  - name: compute_growth
    description: Calculates period-over-period growth (MoM or YoY) for a specific ward and category without unauthorized aggregation.
    input: Filtered row list, growth_type (MoM/YoY), ward (string), category (string).
    output: A list of dicts containing period, actual_spend, growth_pct, formula_used, flag, and notes.
    error_handling: Flags missing values with reason; sets growth to N/A or NULL when prior or current period is missing; refuses cross-ward merging.
