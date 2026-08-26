skills:
  - name: classify_complaint
    description: Classifies a single complaint description string into the required schema (category, priority, reason, flag).
    input: Single string (complaint description).
    output: A structured object/dictionary containing fields: category, priority, reason, flag.
    error_handling: If input is ambiguous, set category to 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads the input CSV file, applies classification to each row, and writes the results to the output CSV.
    input: File path to the input CSV containing raw complaints.
    output: Writes a CSV file with columns: category, priority, reason, flag.
    error_handling: Log parsing errors for individual rows; continue processing the remaining rows in the file.
