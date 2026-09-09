skills:

- name: load_dataset
  description: Reads a target budget CSV file, validates required column structures, and explicitly flags all deliberate null rows along with their notes before returning data.
  input:
  type: string
  format: File path pointing to a budget CSV (e.g., ../data/budget/ward_budget.csv) containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
  output:
  type: object
  format: Validated dataset structure containing tabular data alongside an explicit report of null actual_spend row indices and corresponding note explanations.
  error_handling: Refuses processing and throws an error if the input file path is missing or invalid, required schema columns are absent, or data type constraints are violated.

- name: compute_growth
  description: Calculates per-period spend growth for a specific ward and category combination, explicitly reporting formulas used and flagging null spend values without computing them.
  input:
  type: object
  format: Structured arguments including ward (string), category (string), and growth_type (string, e.g., MoM).
  output:
  type: string
  format: Per-ward per-category CSV table (e.g., uc-0c/growth_output.csv) containing actual spend, calculated growth percentages, explicit null flags, and displayed formula strings.
  error_handling: Refuses execution and requests parameters if growth_type is omitted, or if requested to calculate an all-ward or all-category aggregation without explicit instruction.
