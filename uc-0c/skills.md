skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the columns, parses rows, and logs/reports all occurrences of null actual spend values.
    input: String path to the CSV file.
    output: A list of dicts representing valid rows.
    error_handling: Handles missing file or malformed CSV, and tracks null values in the data.

  - name: compute_growth
    description: Filters budget rows by ward and category, sorts them chronologically, and calculates the MoM growth, formatting the growth percentage and formula used.
    input: A list of dicts (records), ward string, category string, and growth type string.
    output: A list of dicts representing the computed growth table.
    error_handling: Refuses execution if ward or category is empty/All, or if growth type is not specified. Outputs NULL growth and reports null reasons if values are missing.
