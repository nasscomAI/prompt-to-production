# skills.md

skills:

* name: classify_complaint
  description: Classifies one complaint into a category and priority.
  input: A single complaint row from the CSV as a dictionary.
  output: A dictionary containing complaint_id, category, priority, reason, and flag.
  error_handling: If classification is ambiguous, return category "Other" and flag "NEEDS_REVIEW". Never crash on missing values.

* name: batch_classify
  description: Reads the input CSV, classifies every complaint, and writes the results CSV.
  input: Input CSV file path and output CSV file path.
  output: A CSV containing complaint_id, category, priority, reason, and flag for every row.
  error_handling: Continue processing if a row fails. Record the failure with an appropriate flag instead of stopping the program.
