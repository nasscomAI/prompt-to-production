# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the count and details of null actual_spend rows before returning the data.
    input:
      type: CSV file path
      format: String (path to ../data/budget/ward_budget.csv)
    output:
      type: Structured dataset with metadata
      format: Object containing rows, column validation status, null count, and list of null row indices with notes
    error_handling: >
      If the file is missing, columns are invalid, or the format is ambiguous, returns an error specifying the issue. If nulls are present, always reports their count and details before returning data.

  - name: compute_growth
    description: Computes per-period growth for a specified ward, category, and growth_type, showing the formula used in every output row.
    input:
      type: Object
      format: { ward: String, category: String, growth_type: String, dataset: Structured dataset }
    output:
      type: Per-period growth table
      format: Table with columns: period, actual_spend, growth_value, formula_used, null_flag (if applicable), null_reason (if applicable)
    error_handling: >
      If ward or category is missing or ambiguous, or if growth_type is not specified, refuses and requests clarification. If any row has null actual_spend, flags it and reports the null reason from notes. If asked to aggregate across wards or categories, refuses and explains the rule.
