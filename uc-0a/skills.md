skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a specific category, priority, reason, and flag.
    input: A string containing the text of a single citizen complaint description.
    output: A structured record containing category (string, from allowed list), priority (Urgent, Standard, Low), reason (one sentence string citing specific words), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is genuinely ambiguous or cannot be confidently classified into the allowed categories, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes an input CSV file of complaints by applying the classify_complaint skill to each row and writing the results to an output CSV.
    input: Path to an input CSV file (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Path to an output CSV file (e.g., uc-0a/results_[your-city].csv) containing the classified rows.
    error_handling: If individual row classifications fail or input is invalid, log the error and ensure the output file is still generated for successfully processed rows.
