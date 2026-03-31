# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into its proper category, priority level, justification reason, and possible review flag.
    input: A single complaint row containing a description string.
    output: Returns category, priority, reason, and flag values for the complaint.
    error_handling: If the complaint description is ambiguous or lacks sufficient detail, assign category as "Other" and set the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads the input CSV of complaints, applies classify_complaint to each row, and writes the processed output to a new CSV file.
    input: The input CSV file path (e.g., "../data/city-test-files/test_[your-city].csv").
    output: The output CSV file path (e.g., "results_[your-city].csv").
    error_handling: Log errors for missing input files or formatting issues. For row-level failures, skip or flag malformed rows and proceed with processing the remaining rows.
