# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to determine its category, priority, and justification.
    input: A dictionary containing 'description' and 'complaint_id'.
    output: A dictionary with 'category', 'priority', 'reason', and 'flag'.
    error_handling: Returns 'Other' category and 'NEEDS_REVIEW' flag if input is malformed or extremely vague.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and saves the results to a new CSV.
    input: Input CSV path and output CSV path.
    output: None (writes to file).
    error_handling: Logs failures per row but continues processing the rest of the file.
