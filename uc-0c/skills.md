# skills.md

skills:

  - name: load_dataset
    description: Reads the CSV dataset, validates the presence and types of all required columns, and reports details of any null values found in the actual spend.
    input: A string representing the file path to the input CSV file.
    output: A dictionary or dataframe containing the parsed records, accompanied by a report detailing the number of null actual_spend rows, their indices, and their corresponding notes.
    error_handling: Raise FileNotFoundError if the input CSV does not exist. Raise ValueError if any required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or if the format is invalid.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category using the specified growth type (e.g., MoM or YoY) and shows the formula used.
    input: A dictionary or dataframe containing the parsed records, a string for the target ward, a string for the target category, and a string representing the growth type.
    output: A list or table (such as a CSV representation) containing the periods, actual spend, computed growth, and the formula used for each period, with null periods flagged and not computed.
    error_handling: Raise ValueError if the requested ward or category does not exist in the dataset, if the growth type is not supported/specified, or if growth computation is attempted on null actual_spend values.
