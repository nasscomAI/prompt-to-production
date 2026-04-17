# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint by assigning category, priority, reason, and flag.
    input: Complaint row as a dictionary/object with at least a 'description' field (string).
    output: Dictionary/object with fields: category (string), priority (string), reason (string), flag (string or blank).
    error_handling: If category cannot be determined from the description, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path (string), Output CSV file path (string).
    output: Output CSV file with columns: category, priority, reason, flag, matching the schema.
    error_handling: Skips rows with missing or invalid descriptions, logs or flags them for review in the output.
