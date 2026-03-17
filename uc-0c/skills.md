# skills.md

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: file path or dataset to read
    output: parsed dataset and a report of null values mapping to their rows
    error_handling: System must report missing `actual_spend` values and extract the reason from `notes` column instead of silently inferring or skipping.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: ward, category, growth_type (MoM, YoY)
    output: per-period table including a column showing the formula used alongside the calculated growth
    error_handling: System must refuse and ask if growth_type is not given (never guess). Refuse all-ward aggregation unless explicitly told.
