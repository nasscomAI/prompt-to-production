skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates the column structure, and identifies any rows with null actual_spend values along with their notes.
    input: Path to the CSV file (string).
    output: A list of dictionaries representing the budget rows, and a report of any null rows found.
    error_handling: Raises an error if mandatory columns are missing or if the file cannot be loaded.

  - name: compute_growth
    description: Takes a filtered dataset for a specific ward and category, and calculates the period-on-period growth (e.g. MoM) while flagging null values and displaying the formula used.
    input: Filtered dataset (list of dicts), ward (string), category (string), and growth_type (string).
    output: A list of dictionaries containing period, ward, category, actual_spend, growth, and formula.
    error_handling: Refuses to calculate and flags any null rows with the reason from the notes column.
