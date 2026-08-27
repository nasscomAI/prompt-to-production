skills:
  - name: load_dataset
    description: Reads CSV dataset, validates expected columns, and explicitly reports total null count and which specific rows are null before returning.
    input: File path to the target CSV dataset.
    output: Parsed dataset object and a summary report of null rows.
    error_handling: Validates columns and fails if structure is unexpected. It does not crash silently on nulls but returns them for flagging.

  - name: compute_growth
    description: Takes dataset filtered to a specific ward and category, and a growth_type, to compute a per-period table with the applied formula shown.
    input: Filtered dataset, ward name, category name, and growth_type (MoM or YoY).
    output: Per-period table containing period, growth calculation result, and the explicit formula used.
    error_handling: If `growth_type` is missing or ambiguous, refuse and ask. If multiple wards or categories are in the filtered data, refuse to aggregate.
