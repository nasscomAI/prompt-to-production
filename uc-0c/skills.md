skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and reports any null count and their exact rows before returning the data.
    input: File path to the budget data CSV.
    output: A list of dictionaries representing the validated dataset.
    error_handling: Must raise an exception if required columns are missing. Must explicitly flag and report rows with null actual_spend before returning.

  - name: compute_growth
    description: Takes the dataset, ward, category, and growth type, and returns a per-period table showing the calculated growth and formula used.
    input: A dictionary containing the dataset, target 'ward' string, target 'category' string, and 'growth_type' string.
    output: A list of dictionaries with the computed growth for each period.
    error_handling: If growth_type is missing, refuse calculation and prompt the user. If asked to compute across multiple wards or categories without explicit instruction, refuse immediately.
