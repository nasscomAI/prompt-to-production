skills:
  - name: classify_complaint
    description: Takes one complaint dictionary, evaluates text triggers, assigns category, priority, reason, and flag.
    input: Dictionary representing a single complaint row (must include complaint_id, description, location, etc.).
    output: Dictionary with original row fields plus category, priority, reason, and flag.
    error_handling: If input row is malformed or missing key fields, default category to Other, priority to Low, reason to 'Missing description', and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint row by row, and writes the results to an output CSV file.
    input: Input CSV file path (e.g. test_pune.csv) and Output CSV file path (e.g. results_pune.csv).
    output: Writes output CSV file containing classified complaints with all schema columns.
    error_handling: Handles missing input files gracefully, flags malformed rows, and ensures execution continues across all rows.
