# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required columns, identifies null actual_spend rows, and returns structured rows for processing.
    input: File path (string) to the CSV dataset.
    output: A list of row dictionaries and a report of null row counts and details.
    error_handling: If the file is missing or required columns are absent, raise FileNotFoundError or ValueError.

  - name: compute_growth
    description: Computes per-period growth for a specified ward, category, and growth type, with formula details shown for each output row.
    input: Ward (string), category (string), growth_type (string, e.g. MoM), and loaded dataset rows.
    output: A per-period table of growth results including formula, values, and null flags.
    error_handling: If growth_type is missing or invalid, raise ValueError; if ward/category selection is ambiguous or missing, refuse rather than guess.
