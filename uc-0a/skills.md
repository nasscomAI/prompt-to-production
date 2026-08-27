# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description to determine its category and priority.
    input: String - The raw text of a citizen complaint.
    output: JSON - {category: String, priority: String, reason: String, flag: String}
    error_handling: If description is null/empty or genuinely ambiguous, category: 'Other', flag: 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads the city's input CSV file, applies classify_complaint to each row, and writes the results to the output file.
    input: CSV - A file containing 'id' and 'description' columns at the input_path.
    output: CSV - A file containing 'id', 'description', 'category', 'priority', 'reason', and 'flag' at the output_path.
    error_handling: Skips rows with missing IDs; logs a warning if a description is missing but continues processing the rest of the batch.
