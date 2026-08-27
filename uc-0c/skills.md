# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and explicitly reports the total null count and which specific rows are null before returning the data.
    input: Path to the input CSV file.
    output: Parsed dataset object ready for computation, along with a report of any null values found.
    error_handling: Refuse to proceed silently if nulls are present without flagging them and reporting their context from the notes column.

  - name: compute_growth
    description: Takes the ward, category, and explicitly provided growth_type to calculate growth and returns a per-period table with the formula shown on each row.
    input: Parsed dataset, specific ward string, specific category string, and the explicit growth_type (e.g., MoM or YoY).
    output: A per-period table showing the computed growth and the explicit formula used for each row.
    error_handling: Return an error and refuse to calculate if --growth-type is not provided. Refuse to compute an aggregated number across wards or categories.
