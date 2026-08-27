# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a specific category and priority based on severity keywords, providing a one-sentence justification.
    input: String containing the citizen's complaint description.
    output: Structured data with fields: category (string), priority (string), reason (string), and flag (string).
    error_handling: If the category is genuinely ambiguous, set the category to 'Other' and the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to a new CSV file.
    input: File path to the input CSV (must contain a description column).
    output: File path to the output CSV containing the original data plus category, priority, reason, and flag columns.
    error_handling: Validates that the input file exists and contains the required columns; ensures all output categories match the allowed list.
