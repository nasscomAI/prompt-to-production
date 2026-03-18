skills:

- name: classify_complaint
  description: Classifies a single citizen complaint row into a standardized category, priority, reason, and flag.
  input: Dictionary or string representing one complaint row (containing the description).
  output: Dictionary with keys `category`, `priority`, `reason`, and `flag`.
  error_handling: Return category "Other", flag "NEEDS_REVIEW", priority "Standard", and note ambiguity in reason.

- name: batch_classify
  description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
  input: Input CSV file path and Output CSV file path.
  output: A newly written CSV file containing the classifications.
  error_handling: Log errors for malformed rows and skip or write them with NEEDS_REVIEW flag; ensure file writing does not fail halfway through.
