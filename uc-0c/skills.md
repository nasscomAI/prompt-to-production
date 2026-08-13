skills:
  - name: load_dataset
    description: Read the budget CSV file, validate columns, and detect and report all null actual_spend rows with notes before processing.
    input: Path to the budget CSV file.
    output: A validated dataset object along with a report detailing the count and location of null rows.
    error_handling: Raise an error if required columns are missing, or if the file cannot be opened.

  - name: compute_growth
    description: Compute the growth rate per period for a specific ward and category using the specified growth type, formatting the output with calculations and formulas.
    input: Dataset object, ward name, category name, and growth type (e.g., MoM or YoY).
    output: A per-period table (CSV or structured data) containing the actual spend, calculated growth percentage, and formula string. Null rows must be represented as NULL and display the notes reason.
    error_handling: Refuse execution if ward or category is missing/invalid, or if the growth type is unspecified. If a calculation involves a null spend value, propagate the NULL and flag it with the note.
