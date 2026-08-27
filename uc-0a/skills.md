skills:
  - name: classify_complaint
    description: Analyzes one citizen complaint row and determines its appropriate category, priority, justification reason, and whether it needs human review.
    input: A single citizen complaint description string or row without category and priority.
    output: A structured result containing exactly four fields - category (string), priority (string), reason (one sentence string), and flag (string 'NEEDS_REVIEW' or blank).
    error_handling: When perfectly categorizing is not possible due to genuine ambiguity, it does not guess; it outputs category as 'Other' and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of city complaints, iteratively applies the classify_complaint skill to each row, and writes the classified records to an output CSV file.
    input: Filepath to an input CSV containing complaints (e.g., ../data/city-test-files/test_[your-city].csv).
    output: A newly generated CSV file at a specified path (e.g., uc-0a/results_[your-city].csv) with appended columns for category, priority, reason, and flag.
    error_handling: If a row is malformed or unprocessable, logs the failure and gracefully continues to the next row to ensure the batch output file is still generated.

    example output file: uc-0a/results_[your-city].csv

    example final command: python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv
