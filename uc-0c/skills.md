# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: "load_dataset"
    description: "Loads the ward budget CSV, validates columns, and identifies all rows with null 'actual_spend' values."
    input: "Path to the budget CSV file."
    output: "A filtered dataset and a report of pre-identified null gaps with their reasons."
    error_handling: "Refuse to proceed if 'actual_spend' is missing without a corresponding note."

  - name: "compute_growth"
    description: "Calculates MoM growth for a specific ward/category pair, ensuring null rows correctly interrupt the time series with a status flag."
    input: "Ward name, Category name, Growth type (MoM), and the filtered dataset."
    output: "A CSV-ready list of records with 'period', 'actual_spend', 'growth_percentage', and the 'formula' used."
    error_handling: "If growth type is not 'MoM', throw an error and ask the user for the specific growth metric."
