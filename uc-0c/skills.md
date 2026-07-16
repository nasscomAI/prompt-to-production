# skills.md

skills:
  - name: load_dataset
    description: Reads the input CSV budget data, validates the columns, and reports the locations and count of any null actual spend values.
    input: Path to the input budget CSV file.
    output: A list of dictionary objects representing the rows, along with a warning log of null actual spend rows.
    error_handling: Refuses to process if columns are missing or if the file format is incorrect.

  - name: compute_growth
    description: Computes period-over-period budget spend growth (MoM) for a specific ward and category, returning a table with spend, growth percentage, and formula.
    input: Loaded dataset, ward name, category name, and growth type (MoM).
    output: A table or structured file showing period, actual spend, growth, and the formula used for each computation.
    error_handling: Refuses to calculate growth if either the current or prior period has a null spend, and flags the null row stating the reason from notes.
