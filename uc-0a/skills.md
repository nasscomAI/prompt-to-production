# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag
    input: A dictionary containing complaint_id and description
    output: A dictionary with complaint_id, category, priority, reason, and flag
    error_handling: If description is missing or unclear, return category=Other and flag=NEEDS_REVIEW

  - name: batch_classify
    description: Reads a CSV file and applies classification to each complaint row
    input: Path to input CSV file
    output: Output CSV file with classification results
    error_handling: Continues processing even if some rows fail, marking them with flag=ERROR
