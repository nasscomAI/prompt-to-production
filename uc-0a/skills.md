# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into predefined categories, determines priority, extracts reasoning, and sets a review flag.
    input: Dictionary containing 'complaint_id' and 'description' (strings).
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag' (strings).
    error_handling: If input format is invalid or cannot be classified, return 'category' as 'Other', 'priority' as 'Standard', 'reason' as 'Failed to classify.', and 'flag' as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the structured results to an output CSV.
    input: Input file path (string) and output file path (string).
    output: Writes parsed data directly to the specified output CSV path. Returns nothing.
    error_handling: Discards or skips rows that cannot be read, but processing must not crash; writes successful classifications to output even if some rows fail.
