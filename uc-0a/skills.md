# skills.md

skills:
  - name: classify_complaint
    description: Receives one complaint row and classifies it, returning category, priority, reason, and flag fields.
    input: A single citizen complaint text description string.
    output: A record/object containing the fields category (string), priority (string), reason (string), and flag (string).
    error_handling: Return flag as NEEDS_REVIEW and category as Other if the input cannot be processed or is ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill row-by-row, and writes the output to a new CSV file.
    input: File path to the input CSV containing complaints.
    output: File path to the generated output CSV with classification results.
    error_handling: Raise/log an error and halt if the input CSV file is missing or unreadable.
