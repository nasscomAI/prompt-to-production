skills:
  - name: load_dataset 
    description: Reads the CSV data, validates the schema, and reports the total count and exact locations of any null values before returning the dataset.
    input: 
        type: string 
        format: Absolute or relative file path to the CSV dataset.
    output: 
        type: object 
        format: Parsed dataset structure containing the data rows alongside a report detailing any null values found.
    error_handling: 
        Fails if the dataset structure is malformed or missing expected columns; explicitly flags every null row and reports the reason from the notes column rather than silently dropping or filling nulls.

  - name: compute_growth 
    description: Computes the requested growth metric for a specific ward and category over time, outputting a period-by-period table with explicit formulas.
    input: type: object format: Key-value mapping containing ward (string), category (string), and growth_type (string). 
    output: type: array format: Per-period table where each row includes the period, actual spend, calculated growth, and the formula used to compute it. 
    error_handling: Refuses to execute and prompts the user if growth_type is not provided (never guesses a default); refuses any request to aggregate across multiple wards or categories; flags any null rows with their reason instead of computing growth for them.
