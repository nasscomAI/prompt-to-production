skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: string representing the CSV file path
    output: Validated structured dataset, including a pre-computation report detailing null count and specific rows with missing values
    error_handling: Immediately fail and report if dataset format does not match expected ward budget schema or if file is unreadable.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Validated dataset object, string ward, string category, string growth_type (e.g., "MoM", "YoY")
    output: Per-period table containing period, actual spend, calculated growth percentage, and string formula text
    error_handling: Refuse execution if growth_type is missing, or if attempting to compute growth over a null row, or if attempting to aggregate multiple wards/categories without explicit instruction.
