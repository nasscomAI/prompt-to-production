skills:
  - name: load_dataset
    description: Reads the budget CSV, validates all required columns, and reports the null count and specific rows with missing values before returning the data.
    input: File path to the target CSV dataset (string).
    output: Parsed dataset alongside a validation summary specifying the total number of null values and exactly which periods/rows contain them.
    error_handling: Raises a validation error if the file is unfound or required columns are missing, explicitly detailing what is absent.

  - name: compute_growth
    description: Takes the ward, category, and growth_type to calculate growth metrics, returning a per-period table that shows the formula used and handles missing data.
    input: Parsed dataset, ward (string), category (string), and growth_type (string, e.g., 'MoM', 'YoY').
    output: A per-period table presenting the period, actual spend, calculated growth, and the formula used for each row.
    error_handling: Immediately refuses and asks the user for clarification if growth_type is missing. Flags null rows with their reason from the notes column instead of computing a value or erroring out.
