skills:
  - name: classify_complaint
    description: Classify a single complaint row into a standardized category, determine priority based on severity keywords, provide a reason, and flag if ambiguous.
    input: Dictionary representing a single complaint row, containing at least a 'description' or text field.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If genuinely ambiguous, output category 'Other' and flag 'NEEDS_REVIEW'. If description is null, return flagged defaults.

  - name: batch_classify
    description: Read an input CSV of unclassified complaints, apply classify_complaint to each row, and write the augmented results to an output CSV.
    input: Path to the input CSV string (input_path) and output CSV string (output_path).
    output: A newly written CSV file at the output_path containing the classification results.
    error_handling: Must gracefully handle missing values or unparseable rows without crashing, ensuring valid rows are still processed and written.
