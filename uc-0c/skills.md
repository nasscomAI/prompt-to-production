skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and explicitly reports the count and location of any null rows before returning the data.
    input: File path to the dataset (e.g., `../data/budget/ward_budget.csv`)
    output: Validated dataset ready for computation, alongside a report of any null values found.
    error_handling: Refuses to process if columns are missing or if null rows cannot be identified properly.

  - name: compute_growth
    description: Calculates growth for a specific ward and category using the desired growth type, showing the exact formula used for every row.
    input: Arguments for `ward`, `category`, and `growth_type`.
    output: A per-period table of the computed growth, displaying the result and the formula used alongside it.
    error_handling: Refuses to guess if `growth_type` is missing or if asked to aggregate across wards/categories without explicit instructions.
