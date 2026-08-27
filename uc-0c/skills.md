# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

- name: load_dataset
  description: "Reads the ward budget CSV, validates required columns, and reports all null actual_spend rows before any growth calculation."
  input: "Local filesystem path string to a CSV file, expected format: ../data/budget/ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, and notes."
  output: "Structured dataset object containing typed rows plus a null report with null_count and each null row's period, ward, category, and notes reason."
  error_handling: "Fail with a clear error if the file is missing, unreadable, empty, not a CSV, missing required columns, has invalid period values, has non-numeric budgeted_amount values, or has non-numeric actual_spend values except blanks; treat blank actual_spend as NULL, not zero, and report every NULL row before returning."

- name: compute_growth
  description: "Computes growth for one specified ward and category using the explicitly provided growth_type and returns a per-period table with formulas shown."
  input: "Structured dataset object from load_dataset, exact ward string, exact category string, and explicit growth_type string such as MoM."
  output: "Per-period table rows containing period, ward, category, actual_spend, comparison_period, comparison_actual_spend, growth_type, formula, growth_result or null flag, and status."
  error_handling: "Refuse if ward, category, or growth_type is missing or ambiguous; refuse all-ward or all-category aggregation unless explicitly instructed; never guess a formula; flag rows with NULL current or comparison actual_spend and do not compute those growth values."
