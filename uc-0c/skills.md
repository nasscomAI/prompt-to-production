# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: -  load_dataset 
    description: - Reads the budget CSV file, validates required columns, and reports null counts and affected rows before returning the dataset. 
    input:- CSV file path, format: Must include columns [period, ward, category, budgeted_amount, actual_spend, notes]
    output:Dataset object, format: Structured table with metadata including null count and list of rows with null actual_spend
    error_handling:  If columns are missing or invalid, refuse and report schema mismatch. If file path is invalid, return error message. If null values are present, explicitly list them with reasons from notes column before returning. Never silently drop or impute nulls.

  - name: - compute_growth
    description:Computes growth metrics for a specified ward and category using the given growth_type, returning a per-period table with formulas shown
    input: Parameters, format: ward (string), category (string), growth_type (string: MoM or YoY), dataset object
    output: -  Table, format: Per-period rows including actual spend, growth value, and explicit formula used 
    error_handling:If growth_type is not specified, refuse and request clarification. If ward or category is missing or ambiguous, return error and refuse computation. If actual_spend is null for a period, flag the row and report null reason from notes column without computing growth. If asked to aggregate across wards or categories, refuse and report violation.
