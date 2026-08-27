# skills.md

skills:

- name: classify_complaint
  description: Classifies a single complaint description into category, priority, reason, and flag.
  input: A complaint text string from the CSV file.
  output: category (string), priority (string), reason (one sentence), flag (string or blank).
  error_handling: If the complaint text is unclear or does not match any category, return category "Other" and set flag to "NEEDS_REVIEW".

- name: batch_classify
  description: Processes multiple complaints from a CSV file and writes the classification results to a new CSV.
  input: Input CSV file containing complaint descriptions.
  output: Output CSV file with columns: complaint, category, priority, reason, flag.
  error_handling: Skip empty rows and mark unclear complaints with category "Other" and flag "NEEDS_REVIEW".