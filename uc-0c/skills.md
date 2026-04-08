skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns against expectations, and explicitly reports the null count and the specific rows affected before returning the data.
    input: Valid file path to the CSV dataset (String)
    output: Parsed dataset alongside a report of any null values and their corresponding rows (JSON/Dict)
    error_handling: Return a clear error if the file cannot be accessed, read, or if columns are missing. Stop execution if data is structurally corrupted.

  - name: compute_growth
    description: Takes a specific ward, category, and growth_type, and returns a per-period table showing the calculated growth over time with the exact formula used.
    input: Ward name, category name, growth type (e.g., MoM, YoY), and the parsed dataset (JSON/Dict)
    output: A per-period data table explicitly showing the growth metric alongside the formula used for each row (List/Table)
    error_handling: Return an error and refuse to compute if the growth type is not specified or if the requested ward/category combination requires unauthorized aggregation. Flag any explicitly null actual spend rows without calculating for them.
