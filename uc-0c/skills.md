skills:
  - name: load_dataset
    description: "Loads the budget CSV, validates columns, and generates a pre-calculation report of all null rows found in the data."
    input: "Path to input budget CSV file."
    input_format: File path (string)
    output: "A filtered collection of records for the specific ward and category, along with a 'null_registry' showing missing months and their reasons."
    output_format: Object { records: list, null_registry: list }
    error_handling: "Raises an error if core columns are missing or if the ward/category combination does not exist in the dataset."

  - name: compute_growth
    description: "Calculates the specified growth percentage (MoM or YoY) and embeds the mathematical formula used for each period."
    input: "Growth type (MoM/YoY) and structured dataset records."
    input_format: String and Object
    output: "A final list of growth records with columns for period, actual_spend, growth_pct, and formula_shown."
    output_format: List of Objects
    error_handling: "Returns 'NULL_DATA' and the corresponding note if any point in the growth calculation involves a null value."
