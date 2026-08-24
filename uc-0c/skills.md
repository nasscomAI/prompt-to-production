# skills.md

skills:
  - name: load_dataset
    description: Opens the target CSV file, parses the columns, and identifies any missing or null values in the 'actual_spend' column.
    input: File path to the dataset CSV.
    output: A parsed list of structured row objects, alongside a log of how many null rows exist and exactly which ones they are.
    error_handling: Raise an error if the file cannot be accessed or columns are missing.

  - name: compute_growth
    description: Processes the data for a specific ward, category, and growth type, extracting the period-to-period numbers and producing calculated metrics.
    input: Ward name, Category name, Growth type string (e.g. 'MoM'), and the parsed dataset.
    output: A table of results containing the calculated growth metric, the formula used to get it, and any flags about missing data.
    error_handling: Refuse to compute global aggregates if ward/category isn't specified, and refuse to compute if the growth type is absent or unrecognized.
