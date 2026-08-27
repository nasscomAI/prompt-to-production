# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its specific category, priority, reason, and an ambiguity flag.
    input: A single citizen complaint description (text string).
    output: A structured classification object containing 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: If the input is invalid or genuinely ambiguous, fallback to category 'Other', set flag 'NEEDS_REVIEW', and state the ambiguity in the reason.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Filepath to an input CSV file containing citizen complaints.
    output: Writes structured classification results to an output CSV file and returns completion status.
    error_handling: If an individual row fails to map cleanly, mark identically as 'NEEDS_REVIEW' and category 'Other', log the local failure, and continue processing the rest of the batch.
