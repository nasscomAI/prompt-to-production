skills:
  - name: load_dataset
    description: Loads the ward budget CSV dataset, validates required columns, and identifies null rows before computation.
    input: File path to CSV dataset (string)
    output: Tuple containing dataset (list of dictionaries) and list of rows with null actual_spend values
    error_handling: Raises error if file is missing, unreadable, or required columns are not present

  - name: compute_growth
    description: Computes month-over-month (MoM) growth for a specified ward and category with explicit formula output.
    input: Dataset (list of rows), ward name (string), category name (string), growth type (string)
    output: List of dictionaries containing period, actual_spend, growth percentage, and formula used
    error_handling: 
      - If growth-type is missing or invalid, raises error and stops execution  
      - If actual_spend is null, skips calculation for that row and flags it with reason  
      - If insufficient previous data exists, marks growth as N/A