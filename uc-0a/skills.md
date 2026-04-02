# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Receives one complaint row and outputs the classification (category, priority, reason, flag).
    input: Dictionary representing a single CSV row of the complaint.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: Refuses to guess on ambiguous complaints by setting category to 'Other' and flag to 'NEEDS_REVIEW'. Returns 'Other' for unknown types.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to each row, and writes the output CSV.
    input: String path to the input CSV file and string path to the output CSV file.
    output: None (writes to a file).
    error_handling: Handles nulls explicitly and does not crash on bad rows, continuing to produce output for the remaining valid rows.
