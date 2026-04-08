skills:

* name: classify_complaint
  description: Classifies a single citizen complaint description into category, priority, reason, and flag according to the allowed taxonomy and severity rules.
  input: A dictionary representing one complaint row from the CSV file containing fields such as complaint_id and description.
  output: A dictionary containing complaint_id, category, priority, reason, and flag.
  error_handling: If the description is missing or unclear, the function returns category as "Other", priority as "Low" or "Standard", and sets flag to "NEEDS_REVIEW".

* name: batch_classify
  description: Reads the input CSV file, applies classify_complaint to each complaint row, and writes the results to an output CSV file.
  input: Path to the input CSV file containing complaint records.
  output: A CSV file containing classification results with columns complaint_id, category, priority, reason, and flag.
  error_handling: If a row contains invalid or malformed data, the row is still written to the output with category "Other" and flag "NEEDS_REVIEW" instead of crashing the program.

