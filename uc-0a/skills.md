# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a specific category, priority, reason, and flag using exactly the allowed schema.
    input: A single citizen complaint description string.
    output: A structured object containing exactly four fields - `category`, `priority`, `reason`, and `flag`.
    error_handling: If the complaint description is genuinely ambiguous and cannot be confidently classified, sets the `flag` field to "NEEDS_REVIEW" and classifies category as "Other" (or best guess if restricted). Avoids hallucinating categories.

  - name: batch_classify
    description: Reads an input CSV file containing city citizen complaints, processes each complaint using the classify_complaint skill, and writes the results to an output CSV file.
    input: Filepath to an input CSV file of citizen complaints.
    output: A newly generated output CSV file containing the resulting classifications.
    error_handling: If a specific row fails to process or is malformed, logs the error, safely skips the row, and continues processing the remainder of the batch.
