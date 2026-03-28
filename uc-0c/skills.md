skills:
  - name: "load_dataset"
    description: "Safely reads the input CSV containing budget data, filters by ward and category, and establishes valid data boundaries."
    input: "Path to the input CSV file, target ward name, and target category name."
    output: "A chronologically sorted list of record dictionaries, ensuring valid ward and category limits."
    error_handling: "Raises an exception if the file cannot be accessed. Checks if requested ward/category exists in the data and refuses invalid entries by raising a ValueError."

  - name: "compute_growth"
    description: "Calculates the strict Month-over-Month (MoM) growth using exact mathematical formulas without inference mapping."
    input: "A chronological list of dictionary records containing 'actual_spend' values."
    output: "A calculated mapping with appended 'mom_growth' fields ready for export."
    error_handling: "Checks for missing or null actual spend values and explicitly raises an error to prevent silent null computation. Fails when numeric parsing breaks."
