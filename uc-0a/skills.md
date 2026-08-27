# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on a fixed taxonomy and rules for urgency.
    input: CSV row dictionary containing 'description', 'location', etc.
    output: Dictionary with 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Sets 'Other' and 'NEEDS_REVIEW' if the category is ambiguous or data is missing.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and writes the results to a new CSV.
    input: Input CSV file path and output CSV file path.
    output: Success message confirming results written to output path.
    error_handling: Handles null fields, bad row formats, and ensures execution even if some rows fail.
