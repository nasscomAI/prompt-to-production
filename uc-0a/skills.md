skills:
  - name: classify_complaint
    description: Analyzes one complaint row and outputs its assigned category, priority, reason, and flag.
    input: Dictionary representing a single complaint row containing the text description.
    output: Dictionary with exactly four keys: 'category', 'priority', 'reason', 'flag'.
    error_handling: Set category to "Other", flag to "NEEDS_REVIEW", and provide a valid reason string when the input description is ambiguous or missing.

  - name: batch_classify
    description: Reads an input CSV, processes each row via classify_complaint, and writes results to an output CSV.
    input: Two strings representing file paths (input_path to read from, output_path to write to).
    output: Writes a CSV file containing the classifications to output_path.
    error_handling: Must flag nulls, not crash on invalid/bad rows, and guarantee output CSV generation even if some rows fail.
