# Complaint Classifier Skills

## classify_complaint
- **Input:** Single complaint row (dict/object)
- **Task:** Apply the Complaint Classifier Agent's RICE rules to determine the category, priority, reason, and flag.
- **Output:** A dictionary with `complaint_id`, `category`, `priority`, `reason`, and `flag`.

## batch_classify
- **Input:** Input CSV path, Output CSV path
- **Task:** 
  1. Read the input CSV.
  2. For each row, call `classify_complaint`.
  3. Aggregate results into a list.
  4. Write the results to the output CSV with the required columns.
- **Output:** Completion status and output file path.
