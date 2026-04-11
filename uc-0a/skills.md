# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category, priority, and reason based on specific keywords and taxonomy rules.
    input: A dictionary representing a row from the input CSV (must contain 'description').
    output: A dictionary with 'category', 'priority', 'reason', and 'flag' keys.
    error_handling: Sets 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW' if the description is ambiguous or doesn't match known patterns.

  - name: batch_classify
    description: Orchestrates the classification of all reports in an input CSV file and writes the results to an output CSV.
    input: Two strings representing the input file path and output file path.
    output: None (writes to local filesystem).
    error_handling: Handles missing files and ensures processing continues if individual rows are malformed.
