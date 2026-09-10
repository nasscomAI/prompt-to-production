skills:

* name: "load_dataset"
  description: "Reads the ward budget CSV, validates its required columns, and reports all null actual_spend rows before returning the dataset."
  input:
  type: "file"
  format: "CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns."
  output:
  type: "object"
  format: "Validated dataset plus null_count and a list of every row with null actual_spend, including period, ward, category, and the null reason from notes."
  error_handling:
  invalid_input: "Reject the dataset if the CSV is missing, unreadable, malformed, empty, or lacks any required column."
  null_handling: "Identify every null actual_spend value before returning the dataset; never convert null to zero or another value."
  null_reason: "For every null actual_spend row, report the corresponding reason from the notes column."
  failure_mode: "Do not silently omit null rows or return the dataset without reporting the null count and affected rows."

* name: "compute_growth"
  description: "Computes growth for the explicitly requested ward and category and returns a per-period table with the formula used for every result."
  input:
  type: "object"
  format: "Object containing ward, category, growth_type, and the validated dataset."
  output:
  type: "table"
  format: "Per-period table scoped to the requested ward and category, containing period, actual_spend, growth result, formula used, and null/status information where applicable."
  error_handling:
  invalid_input: "Reject the computation if ward, category, growth_type, or the required dataset is missing or invalid."
  missing_growth_type: "Refuse and ask for growth_type when it is not specified; never assume MoM, YoY, or another formula."
  aggregation_failure: "Refuse requests that aggregate across wards or categories unless such aggregation is explicitly instructed."
  null_handling: "Flag every null actual_spend row before computing and report its null reason from the notes column; do not compute growth for a null value."
  formula_assumption: "Use only the explicitly requested growth_type and show the corresponding formula alongside every output row."
  wrong_aggregation_level: "Return a per-ward per-category table and never collapse the requested data into one combined number."
  ambiguous_request: "If a request such as 'Calculate growth from the data' does not specify a growth type or aggregation scope, refuse to guess and request the missing specification."

