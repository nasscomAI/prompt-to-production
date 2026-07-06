# skills.md

skills:
  - name: [classify_complaint]
    description: [Classifies a single citizen complaint based on the taxonomy, assigns a priority level, generates a one-sentence justification, and flags ambiguous records]
    input: Take one row dict from csv
    output: Return same dict with added 'category', 'priority' and 'reason' columns
    error_handling: If the complaint category is ambiguous, cannot be determined from the description alone, or fits multiple categories equally, classify as category: Other and set flag: NEEDS_REVIEW.

  - name: [batch_classify]
    description: [Batch classifies citizen complaints from a CSV file, adding classified results as new columns.]
    input: Read input csv file, loop through each row and call classify_complaint skill
    output: Writes output csv and print summary stats
    error_handling: Handle all exceptions and invalid inputs gracefully. Print error messages and continue processing remaining records.
