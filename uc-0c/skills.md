skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and explicitly flags any null records with their reasons before returning the data.
    input: File path to the dataset (string).
    output: Validated dataset (table/dataframe) along with a report detailing the null count and specific rows with missing values, including reasons from the notes column.
    error_handling: Raises an error if the file is missing or if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category over time, ensuring the formula used is explicitly shown in the output.
    input: Ward (string), category (string), growth_type (string, e.g., MoM or YoY), and the validated dataset.
    output: A per-period table containing the computed growth for the specified ward and category, with the calculation formula explicitly listed in every row.
    error_handling: Refuses to compute and asks the user for input if growth_type is not specified (never guesses). Refuses execution if instructed to aggregate across multiple wards or categories.
