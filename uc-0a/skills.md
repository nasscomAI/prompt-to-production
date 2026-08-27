skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category and priority with a cited reason.
    input: Dictionary representing a single complaint row (e.g., {"description": "..."}).
    output: Dictionary containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: Sets 'flag' to 'NEEDS_REVIEW' and 'category' to 'Other' if the description is genuinely ambiguous; enforces 'Urgent' priority if severity keywords (e.g., injury, child, hospital) are present.

  - name: batch_classify
    description: Processes an entire CSV file of complaints by applying classification to each row and saving the results.
    input: File path to an input CSV containing complaint descriptions.
    output: File path to an output CSV containing the classification schema fields for each row.
    error_handling: Ensures all generated categories strictly match the allowed taxonomy and validates that every output row contains a justification citing the source description.
