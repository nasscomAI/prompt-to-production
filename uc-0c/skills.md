- name: "load_dataset"
  description: "Reads the budget CSV, validates columns, explicitly reports the null count, and identifies specific rows with null values before returning the data."
  input:
    type: "string"
    format: "File path to the .csv dataset"
  output:
    type: "list/array"
    format: "Parsed and validated dataset objects representing rows"
  error_handling: "Must flag and report any null row (e.g., null 'actual_spend') utilizing the 'notes' column. Must fail safely without crashing if file format is corrupted."

- name: "compute_growth"
  description: "Computes financial growth metrics recursively on a strictly per-ward and per-category level across standard defined periods."
  input:
    type: "object/parameters"
    format: "Key-value pairs specifying 'ward', 'category', and 'growth_type'"
  output:
    type: "table/list"
    format: "Per-period table that explicitly shows the result and the exact formula used for every row"
  error_handling: "Must Refuse execution if asked to aggregate across wards or categories. Must Refuse and ask for clarification if 'growth_type' is omitted instead of guessing the formula type quietly."
