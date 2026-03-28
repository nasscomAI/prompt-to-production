# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag according to strict schema and enforcement rules.
    input: Dictionary representing a complaint row (with at least complaint_id and description fields).
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If the description is missing or ambiguous, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path (string), Output CSV file path (string).
    output: Output CSV file with classified rows (category, priority, reason, flag).
    error_handling: Flags rows with missing or ambiguous data, does not crash on bad rows, and ensures output is produced even if some rows fail.
