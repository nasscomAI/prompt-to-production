## skills.md

skills:
- name: classify_complaint
  description: Classifies one citizen complaint row into the approved UC-0A category, priority, reason, and review flag schema.
  input: A dictionary representing one CSV row. Expected fields include complaint_id and description; other fields may be present but must not override the description-based classification rules.
  output: A dictionary with exactly these keys: complaint_id, category, priority, reason, flag. category must use the approved category list; priority must be Urgent, Standard, or Low; reason must be one sentence citing complaint wording; flag must be NEEDS_REVIEW or blank.
  error_handling: If the row is missing, malformed, has an empty description, or cannot be classified confidently, return category Other, flag NEEDS_REVIEW, and a reason explaining the issue. Do not raise an exception for bad input. If severity keywords are present in available text, priority must still be Urgent.

- name: batch_classify
  description: Reads an input complaint CSV, applies classify_complaint to every row, and writes a results CSV using the required UC-0A output schema.
  input: input_path as a string path to the stripped test_[city].csv file and output_path as a string path where results_[city].csv should be written.
  output: A CSV file containing one output row per input row with columns complaint_id, category, priority, reason, flag.
  error_handling: If individual rows are invalid or ambiguous, write a NEEDS_REVIEW result for those rows and continue processing the remaining rows. If the input file is missing or unreadable, raise a clear file-level error. The batch process must not stop because of a single bad row.
