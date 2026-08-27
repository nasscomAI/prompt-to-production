# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, maps columns, and scans for intentional null data holes.
    input: CSV file path string.
    output: A collection of data rows.
    error_handling: Explicitly loops and catches blank 'actual_spend' values, alerting the prompt console to log the cause via notes.

  - name: compute_growth
    description: Processes sorted financial data to calculate period variance.
    input: Filtered budget rows per ward/category, and a growth_type string.
    output: Rows containing the computed growth percentages and the hardcoded formula metadata.
    error_handling: Refuses calculation across grouped scopes without permission.
