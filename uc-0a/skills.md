skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to determine its category, priority, reason, and an ambiguity flag.
    input:
      - name: complaint_row
        type: dict
        format: A dictionary representing a single row from the input CSV, expected to contain at least a 'description' key (string) and 'complaint_id' (string).
      - name: classification_schema
        type: dict
        format: A dictionary containing allowed categories (list of strings), severity keywords (list of strings), and rules for priority, reason, and flag.
    output:
      type: dict
      format: A dictionary with keys 'complaint_id' (string), 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: Returns 'Other' for category, 'Low' for priority, and sets 'flag' to 'Null Data - Missing Description Text' if 'description' is empty. Sets 'flag' to 'NEEDS_REVIEW' if category is genuinely ambiguous.

  - name: batch_classify
    description: Reads complaints from an input CSV, applies the 'classify_complaint' skill to each, and writes the results to an output CSV.
    input:
      - name: input_path
        type: string
        format: Path to the input CSV file containing citizen complaints (e.g., "../data/city-test-files/test_pune.csv").
      - name: output_path
        type: string
        format: Path where the results CSV file will be written (e.g., "results_pune.csv").
      - name: classification_schema
        type: dict
        format: A dictionary containing allowed categories (list of strings), severity keywords (list of strings), and rules for priority, reason, and flag.
    output:
      type: None
      format: Writes a CSV file to 'output_path' with original columns plus 'category', 'priority', 'reason', and 'flag'.
    error_handling: Catches and logs errors for individual rows, assigning an 'Error' category/priority/reason and a specific flag to the problematic row, then continues processing other rows. Raises FileNotFoundError if input_path is invalid.

