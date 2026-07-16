skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row to extract and classify the category, priority, reason, and review flag.
    input: Dictionary representing a CSV row with keys like description, location, etc.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Falls back to category 'Other' and sets flag to 'NEEDS_REVIEW' if input is null or category is ambiguous.

  - name: batch_classify
    description: Reads an input CSV containing citizen complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path of the input CSV and output CSV.
    output: Writes output CSV and prints confirmation.
    error_handling: Handles missing inputs, handles empty/null values, and ensures the process completes without crashing on individual row errors.
