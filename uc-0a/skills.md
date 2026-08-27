# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
skills
- name: classify_complaint
  description: Classify a single complaint row into category, priority, reason, and flag
  input:
    type: dict
    format: {description: string}
  output:
    type: dict
    format: {category: string, priority: string, reason: string, flag: string}
  error_handling: >
    If description is missing, empty, or ambiguous, set flag to NEEDS_REVIEW and reason to indicate ambiguity.

- name: batch_classify
  description: Read input CSV, apply classify_complaint to each row, write results to output CSV
  input:
    type: string
    format: path to input CSV file
  output:
    type: string
    format: path to output CSV file with category, priority, reason, and flag
  error_handling: >
    Skip rows with missing description and log a warning. Preserve original row data with flag set to NEEDS_REVIEW.