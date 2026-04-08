skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path to the dataset CSV
    output: Loaded data containing period, ward, category, amounts, and notes
    error_handling: Handles missing data by calculating negative impacts using the notes column and explicitly reporting on null actual_spend rows

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Ward, Category, and Growth Type
    output: Per-period table with growth metrics alongside the explicit formula used
    error_handling: System refuses step and asks if --growth-type is omitted, or if trying to compute across multiple wards or categories unprompted
