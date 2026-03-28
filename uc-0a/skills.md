skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, reason, and flag.
    input: A single citizen complaint row (text description) from the CSV.
    output: A structured object containing category, priority, reason, and flag fields.
    error_handling: If the description is empty, invalid, or ambiguous, return category "Other", flag "NEEDS_REVIEW", standard priority, and a reason explaining why it couldn't be classified.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the structured results to an output CSV.
    input: Filepath to the input CSV file containing citizen complaints.
    output: Filepath to the generated output CSV file containing the classification results.
    error_handling: Logs any rows that fail processing and continues to the next; if the input file is missing or unreadable, aborts and throws a specific error message.
