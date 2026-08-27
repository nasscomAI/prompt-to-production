# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns (period, ward, category, actual_spend), and identifies null entries.
    input: String path to the input .csv file.
    output: A list of dictionaries representing the rows, plus a summary of identified null rows and their reasons.
    error_handling: Refuses to proceed if required columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates growth (MoM) for a specific ward and category while adhering to null-handling and formula rules.
    input: 
      data: List of row dictionaries.
      ward: Selected ward name.
      category: Selected category name.
      growth_type: The type of growth (e.g., "MoM").
    output: List of dictionaries containing period, actual_spend, growth_value, formula, and flags for null reasons.
    error_handling: Returns [DATA_MISSING] for null rows and refuses to compute if the input data for the selected filter is empty.
