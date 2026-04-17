# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, reason, and any need for review.
    input: A string representing a single citizen complaint description.
    output: A structured object/row containing exactly four fields - category (exact string match from allowed 10), priority ('Urgent', 'Standard', or 'Low'), reason (one sentence citing specific words), and flag ('NEEDS_REVIEW' or blank).
    error_handling: If the category is genuinely ambiguous, set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: A file path string pointing to the input CSV containing complaints (e.g., ../data/city-test-files/test_[your-city].csv).
    output: A file path string pointing to the generated output CSV (e.g., uc-0a/results_[your-city].csv) containing all classified rows.
    error_handling: If the input file is unreadable or missing, raise an error. If a row is malformed, log the error and continue to the next row.
