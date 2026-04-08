# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint by category, priority, reason, and flag.
    input: Complaint row as a dictionary or object with at least a 'description' field (string).
    output: Dictionary/object with fields: 'category' (string), 'priority' (string), 'reason' (string), 'flag' (string or blank).
    error_handling: If the complaint is ambiguous, sets 'flag' to 'NEEDS_REVIEW'. If input is invalid, returns an error or empty fields.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path (string), output CSV file path (string).
    output: Output CSV file with columns: 'category', 'priority', 'reason', 'flag' for each input row.
    error_handling: Skips or flags rows with invalid or missing data; logs errors or sets 'flag' as needed.
