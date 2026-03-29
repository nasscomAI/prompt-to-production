skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates schema, reports and returns null rows with notes.
    input: |
      Path to CSV file with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: |
      Records list and a report: total rows, null count, and explicit null row keys with notes.
    error_handling: |
      - If file missing or malformed schema: return error flag and empty records.
      - Coerce actual_spend to float when present; treat empty as null.

  - name: compute_growth
    description: Computes per-period growth for a given ward+category using MoM or YoY, with formula.
    input: |
      Records from load_dataset, ward string, category string, growth_type in {MoM, YoY}.
    output: |
      Per-period table with: period, ward, category, actual_spend, comparator_period,
      comparator_actual, growth_value, growth_percent, formula, flag, notes.
    error_handling: |
      - If ward or category not provided: refuse; do not aggregate.
      - If growth_type not provided or unsupported: refuse and request a valid type.
      - If current or comparator actual is null: do not compute; set flag and include notes.
