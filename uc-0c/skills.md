# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates mandatory columns, and inspects the dataset for null actual_spend entries.
    input:
      type: file_path
      format: CSV file path containing columns (period, ward, category, budgeted_amount, actual_spend, notes)
    output:
      type: structured_dataset
      format: Validated list of records along with null row metadata and count
    error_handling: Raises an error if the file is missing or required columns are absent; explicitly identifies and logs all rows with missing actual_spend along with their notes.

  - name: compute_growth
    description: Computes period-over-period spend growth for a specific ward and category while enforcing explicit formula logging and null flagging.
    input:
      type: parameters
      format: Dataset records, ward string, category string, and explicit growth_type (e.g., MoM)
    output:
      type: tabular_data
      format: List of records containing period, ward, category, actual_spend, growth_rate, formula, and status/flag notes
    error_handling: Refuses calculation if growth_type is missing or invalid; refuses cross-ward/category aggregations; skips calculation on null rows and marks them flagged with the underlying reason.
