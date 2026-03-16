skills:
  - name: classify_complaint
    description: Processes a single complaint description string to determine its category, priority, reason, and review flag.
    input: A single string containing the citizen complaint description.
    output: A dictionary or structured object with `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the complaint description is empty or completely unreadable, set category to "Other", priority to "Low", reason stating "Invalid input", and flag to "NEEDS_REVIEW". If ambiguous, set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, processes each row using classify_complaint, and writes the results to an output CSV file.
    input: File path to the input CSV containing complaint rows (with at least a description column).
    output: Writes an output CSV file to the file system containing the original data plus the new classification fields.
    error_handling: Logs any rows that cause processing errors, skips them or writes a failed row with default "Other" and "NEEDS_REVIEW" flags, and continues processing the rest of the file.
