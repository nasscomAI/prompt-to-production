skills:

* name: classify_complaint
  description: Classifies one citizen complaint into the required category and priority while producing a grounded reason and review flag.
  input: A Python dictionary representing one complaint CSV row, including complaint_id and description fields.
  output: A Python dictionary containing complaint_id, category, priority, reason, and flag.
  error_handling: If the description is missing, empty, or genuinely ambiguous, return category Other, set flag to NEEDS_REVIEW, and provide a reason explaining the problem; never crash the batch process.

* name: batch_classify
  description: Reads a complaint CSV file, classifies every row using classify_complaint, and writes the classification results to an output CSV file.
  input: Input CSV file path and output CSV file path as strings.
  output: A CSV file containing complaint_id, category, priority, reason, and flag for every input row.
  error_handling: Handle missing or malformed row data without stopping the entire batch; produce an output row with Other and NEEDS_REVIEW when a complaint cannot be classified safely.
