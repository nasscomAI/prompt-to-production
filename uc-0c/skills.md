# skills.md

skills:
  - name: load_dataset
    description: Reads a CSV file, validates its columns, and explicitly reports the exact count and locations of all null values before returning the parsed dataset.
    input: File path string to a `.csv` data file.
    output: A properly parsed and structured dataset object alongside a preliminary manifest detailing any rows containing null values and their corresponding 'notes'.
    error_handling: System fails and returns an error if the CSV is missing, malformed, or if expected columns (like 'actual_spend' or 'notes') are absent.

  - name: compute_growth
    description: Calculates row-by-row growth for a specific subset of data based strictly on a provided `--growth-type`, displaying the applied formula directly in the output format.
    input: Parsed dataset subset (filtered strictly by ward and category) and an explicit `growth_type` string (e.g., 'MoM').
    output: A per-period table output (e.g., CSV format) containing the computed growth percentages and a column explicitly displaying the formula used. Returns `NULL` values unchanged but flagged.
    error_handling: REFUSES operation if the requested aggregation spans multiple wards or categories without explicit permission, or if the `growth_type` is ambiguous or missing.
