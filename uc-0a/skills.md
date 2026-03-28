# skills.md
skills:

* name: classify_complaint
  description: Classifies one complaint row into category, priority, reason, and flag.
  input: complaint row text
  output: category, priority, reason, flag
  error_handling: returns NEEDS_REVIEW when complaint is ambiguous

* name: batch_classify
  description: Reads input CSV, applies classify_complaint to every row, writes output CSV.
  input: CSV file path
  output: classified CSV file
  error_handling: skips invalid rows or marks them for review
