skills:
  - name: classify_complaint
    description: Classify one citizen complaint into an allowed category and priority with a reason and ambiguity flag.
    input: A dictionary containing complaint_id and complaint description.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the input is missing or invalid, return a safe result using category Other and flag NEEDS_REVIEW; never crash.

  - name: batch_classify
    description: Read a complaint CSV, classify every row, and write the classification results to an output CSV.
    input: An input CSV file path containing complaint rows and an output CSV file path.
    output: A CSV containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Handle missing or malformed rows without crashing, flag uncertain rows for review, and produce an output file even when some rows fail.