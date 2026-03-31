# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and justification.
    input: String (citizen complaint description)
    output: Object { category: string, priority: string, reason: string, flag: string }
    error_handling: If input is ambiguous or non-standard, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints, applying classification to each row and saving the results.
    input: CSV file path (input)
    output: CSV file path (output)
    error_handling: Ensure consistent classification across rows; log any rows that fail to process but continue batch execution.
