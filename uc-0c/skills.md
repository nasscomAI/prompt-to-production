skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path to the CSV dataset (string).
    output: Parsed dataset, plus a summary reporting the total null count and specifically which rows have null actual_spend.
    error_handling: Halts execution if required columns are missing or the file cannot be read.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Dataset, ward (string), category (string), and growth_type (string, e.g., 'MoM').
    output: A per-period table showing the computed growth metric and the exact formula used for every row.
    error_handling: Flags rather than computes rows where actual_spend is null (showing notes). Refuses execution if growth_type is unspecified, missing, or invalid.
