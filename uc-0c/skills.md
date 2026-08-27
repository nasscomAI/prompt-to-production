# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies all null actual_spend rows before processing.
    input: File path (string) to the budget CSV.
    output: A DataFrame or list of dictionaries containing valid rows, along with a report of null rows and their notes.
    error_handling: Raise an error if essential columns are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Calculates growth (MoM and YoY) for a specific ward and category, returning a table that includes the specific formula used for each row.
    input: Ward (string), Category (string), Growth Type (MoM or YoY), and the loaded dataset.
    output: A table or structured list showing period-over-period growth with explicitly detailed formulas.
    error_handling: Refuse and report if the growth type is unspecified or if the requested ward, category combination is not found or 'Any' is passed for ward or category.
