skills:
  - name: classify_complaint
    description: Takes a dictionary representing one complaint row and returns category, priority, reason, and flag adhering to taxonomy and severity rules.
    input: dict containing complaint fields (complaint_id, description, days_open, etc.)
    output: dict containing keys (complaint_id, category, priority, reason, flag)
    error_handling: Flags category as NEEDS_REVIEW if ambiguous or defaults category to Other if unrecognized.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, executes classify_complaint for each row, and writes the structured results to an output CSV file.
    input: input_path (str), output_path (str)
    output: Writes output CSV file with header [complaint_id, category, priority, reason, flag]
    error_handling: Handles empty or invalid input files gracefully without crashing.

