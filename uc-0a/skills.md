# skills.md

skills:

- name: classify_complaint
  description: Classify one citizen complaint row into category, priority, reason, and flag using the strict schema and severity rules.
  input: A dictionary representing one complaint row with fields such as complaint_id and description.
  output: A dictionary with keys all columns from input and in addition to include - complaint_id, category, priority, reason, and flag.
  error_handling: If description is empty or missing or is ambiguous (wherein the classfication is not truly determisnistic) set the flag as NEEDS_REVIEW and set catergory as Other. Don't make assumptions

- name: batch_classify
  description: Read an input CSV, classify each row with classify_complaint, and write the results CSV with the required schema.
  input: Paths to the input CSV file and the output CSV file.
  output: A CSV file containing complaint_id, category, priority, reason, and flag for every input row and also include all columns from input
  error_handling: Continue processing after individual row failures, writing a safe fallback row with Other and NEEDS_REVIEW instead of crashing the batch.
