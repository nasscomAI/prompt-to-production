# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

- name: classify_complaint
  description: Classifies a single complaint description into one of 10 categories with priority level, justification, and ambiguity flag.
  input: Plain text complaint description (string).
  output: CSV row with four fields — category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (single sentence citing specific words from input), flag (NEEDS_REVIEW if ambiguous, blank otherwise).
  error_handling: If category cannot be determined from description alone or genuinely conflicts with boundary definitions, output category as "Other" and set flag to "NEEDS_REVIEW". Never output a low-confidence category.

- name: batch_classify
  description: Reads input CSV file row by row, applies classify_complaint to each complaint, and writes classified output to CSV file.
  input: CSV file path with one complaint per row (minimum: description column; additional columns preserved in output).
  output: CSV file with original columns plus four new columns (category, priority, reason, flag) preserving row order and non-complaint columns.
  error_handling: If a row is malformed or missing description, log error with row number and skip row. If output file cannot be written, raise exception with file path. Continue processing remaining rows even if individual rows fail.
