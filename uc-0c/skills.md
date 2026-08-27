skills:
  - name: load_dataset
    description: Reads the CSV file, validates required columns, and identifies missing data.
    input: File path to the CSV dataset.
    output: A validated dataset object (or list of dictionaries), along with a report detailing the total count of null values and the specific rows where they occur.
    error_handling: Raises an error if required columns are missing and flags all null `actual_spend` rows explicitly using their `notes` before returning data.

  - name: compute_growth
    description: Calculates the requested growth metric (e.g., MoM) for a specific ward and category over time.
    input: Filtered dataset, target ward, target category, and the specified growth_type.
    output: A per-period table (list of rows) showing the period, actual spend, computed growth metric, and the exact formula used.
    error_handling: Refuses to calculate and returns an error if growth_type is missing/unspecified, or if asked to compute across multiple wards/categories without explicit instruction. Applies proper flagging for null calculation periods.
