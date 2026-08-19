# skills.md — UC-0C Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the column schema, and reports every deliberate null actual_spend row with its period, ward, category, and recorded note before any computation.
    input: File path (string) to ward_budget.csv.
    output: A list of row dicts with validated types plus a list of null rows (period, ward, category, notes).
    error_handling: Refuses if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing; explicitly lists all null actual_spend rows with their notes.

  - name: compute_growth
    description: Calculates month-over-month (MoM) growth for one specific ward and category, showing the exact formula used in every output row and never aggregating across wards or categories.
    input: Filtered row list, growth_type (MoM), ward (string), category (string).
    output: A list of dicts containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_pct, formula, flag, and notes.
    error_handling: Refuses all-ward or multi-category requests; refuses when growth_type is missing or unsupported (never guesses MoM vs YoY); flags each null actual_spend row with FLAGGED_NULL, sets growth_pct to NULL, and carries the recorded note; sets growth to N/A when the prior period is unavailable.
