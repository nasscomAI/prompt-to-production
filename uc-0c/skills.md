skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: CSV file path (string)
    output: Parsed dataset (list of dictionaries or DataFrame) and a report of null rows
    error_handling: Raise an error if required columns are missing or if the file cannot be read

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Dataset (from load_dataset), ward (string), category (string), and growth_type (string)
    output: Table (list of dictionaries or DataFrame) containing computed growth and formula shown, explicitly flagging nulls
    error_handling: Refuse and return an error if ward, category, or growth_type are not provided or if asked to aggregate across boundaries
