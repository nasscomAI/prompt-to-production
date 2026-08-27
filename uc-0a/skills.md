# UC-0A Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a predefined category and priority level, providing a justification and a review flag.
    input: A dictionary or object containing the complaint 'description'.
    output: An object with fields 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is blank or the category is ambiguous, set 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and writes the results to a specified output CSV.
    input: Input CSV file path and output CSV file path.
    output: Completion status and the path to the generated results CSV.
    error_handling: Logs errors for missing input files or unreadable CSV rows and continues processing the remaining rows.

