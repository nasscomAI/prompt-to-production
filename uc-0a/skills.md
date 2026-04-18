skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint text to determine its exact civic category and urgency priority.
    input: A single raw complaint text string or row.
    output: A structured object containing the exact keys `category`, `priority`, `reason`, and `flag`.
    error_handling: If the complaint is ambiguous or cannot be definitively categorized, it sets `category` to "Other" and `flag` to "NEEDS_REVIEW".

  - name: batch_classify
    description: Iterates over a dataset to classify complaints in bulk using the `classify_complaint` skill.
    input: A string path pointing to a valid input CSV file containing multiple complaint rows.
    output: A string path pointing to the target written CSV file populated with all verified columns.
    error_handling: Gracefully flags null/empty rows and will not crash the batch execution if a bad row is encountered.
