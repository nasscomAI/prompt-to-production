# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

  - name: classify_complaint
    description: Classify one citizen complaint using the fixed taxonomy and severity rules.
    input: A dictionary containing complaint_id and description strings.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: Return Other with NEEDS_REVIEW for missing, invalid, or ambiguous descriptions.

  - name: batch_classify
    description: Classify every row in an input CSV and write a schema-compliant output CSV.
    input: A CSV path containing complaint_id and description columns, plus an output CSV path.
    output: A CSV with complaint_id, category, priority, reason, and flag columns.
    error_handling: Preserve row order and write Other/NEEDS_REVIEW for rows that cannot be classified.
