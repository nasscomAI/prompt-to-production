# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority level, justification, and ambiguity flag.
    input: A single complaint text description (string).
    output: A structured object containing 'category' (string), 'priority' (Urgent, Standard, Low), 'reason' (string, max 1 sentence), and 'flag' (string or blank).
    error_handling: Refuses to guess if the description is genuinely ambiguous, setting 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a batch of complaints from an input CSV file by sequentially applying the classify_complaint skill to each row.
    input: Path to an input CSV file containing citizen complaint rows.
    output: Writes a new CSV file containing the original columns appended with the classification results.
    error_handling: Wraps row-level errors from classify_complaint by marking the row as 'NEEDS_REVIEW' and moves on to process the remaining rows.
