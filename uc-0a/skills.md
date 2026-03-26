# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A single complaint row containing a 'description' field.
    output: A dictionary containing: category, priority, reason, and flag.
    error_handling: If the description is empty or ambiguous, the category is set to 'Other' and the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and writes results to a new CSV.
    input: A file path to the input CSV.
    output: A file path to the output CSV.
    error_handling: Skips malformed rows and ensures all rows are processed even if individual rows fail classification.
