skills:
  - name: load_dataset
    description: Loads the ward budget dataset and validates required columns.
    input: CSV file path containing ward budget data.
    output: validated dataframe with dataset rows.
    error_handling: raise error if required columns are missing or file cannot be loaded.

  - name: compute_growth
    description: Calculates month-over-month growth for a specified ward and category.
    input: dataframe, ward name, category name, growth type.
    output: table of periods with actual_spend, growth percentage, formula used, and notes.
    error_handling: if actual_spend is null, mark growth as NULL and include the note instead of calculating.