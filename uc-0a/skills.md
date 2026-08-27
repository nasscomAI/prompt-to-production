# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint by outputting an allowed category, a priority level, a reason, and a flag.
    input: A single complaint representation (e.g., a dictionary or text string).
    output: A structured object containing 'category', 'priority', 'reason', and 'flag' fields.
    error_handling: If the complaint description is genuinely ambiguous, assigns flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies the classify_complaint skill to each row, and writes the output to a new CSV.
    input: A CSV file path (e.g., ../data/city-test-files/test_[your-city].csv).
    output: A new CSV file containing classification results (e.g., uc-0a/results_[your-city].csv).
    error_handling: Handles malformed rows by logging errors or skipping them, ensuring the output CSV generation completes for valid rows.
