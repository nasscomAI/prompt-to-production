skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns, and explicitly flags any null values along with their corresponding reasons before returning the data.
    input: A string representing the file path to the source CSV document (e.g., ward_budget.csv).
    output: A structured object (e.g., list of dictionaries) containing the data rows, alongside a distinct report of any rows containing null `actual_spend` values and their `notes`.
    error_handling: Raises a FileNotFoundError if the CSV is missing. If the CSV lacks required columns, it raises a validation error.

  - name: compute_growth
    description: Calculates the specified budget growth metric strictly for a single given ward and category, returning the results alongside the exact mathematical formula used.
    input: The validated dataset, a specific `ward` string, a specific `category` string, and a `growth_type` string (e.g., "MoM").
    output: A per-period data table containing the computed growth and a dedicated column showing the exact formula applied for each row.
    error_handling: If `growth_type` is omitted, the skill refuses to compute and requests clarification. If asked to aggregate across multiple wards or categories, it refuses and throws a scope error. If encountering a null value during computation, it flags the row as uncomputable instead of assuming zero.
