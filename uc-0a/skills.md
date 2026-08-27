skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint record by determining category, priority, reason justification, and review flag according to strict RICE rules.
    input: Dictionary representing a single complaint row with keys 'complaint_id' (string/int) and 'description' (string).
    output: Dictionary containing 'complaint_id', 'category' (exact string from allowed enum), 'priority' ('Urgent', 'Standard', or 'Low'), 'reason' (one sentence citing verbatim text), and 'flag' ('NEEDS_REVIEW' or empty string).
    error_handling: If the complaint description is ambiguous, missing, or cannot be categorized conclusively, set category to 'Other', flag to 'NEEDS_REVIEW', and state the reason instead of failing or guessing.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, iteratively calls classify_complaint for each row, and writes the standardized results to an output CSV file.
    input: File path string for input CSV file (e.g. data/city-test-files/test_[city].csv) and file path string for destination output CSV file (e.g. uc-0a/results_[city].csv).
    output: Writes the output CSV file containing headers 'complaint_id', 'category', 'priority', 'reason', and 'flag', and returns a summary completion status.
    error_handling: Handles file I/O errors, missing columns, and row-level exceptions gracefully without aborting execution, ensuring invalid or corrupt rows are flagged with 'NEEDS_REVIEW' in the output CSV.
