skills:
  - name: classify_complaint
    description: Classify a single complaint record into the required category, priority, reason, and flag format.
    example_invocation:
      call: `classify_complaint({"description": "Large pothole 60cm wide causing tyre damage. Three vehicles affected this week."})`
      returns: `{"category": "Pothole", "priority": "Standard", "reason": "The report specifically mentions a large pothole causing tyre damage.", "flag": ""}`
    input: A dictionary containing the citizen's complaint description string.
    output: A dictionary containing string values for category, priority, reason, and flag.
    error_handling: Return category as "Other" and set flag to "NEEDS_REVIEW" if the input description is missing, invalid, or ambiguous.

  - name: batch_classify
    description: Reads an input CSV, iteratively applies classify_complaint to every row, and writes the output to a results CSV.
    run_command: |
      python classifier.py \
        --input ../data/city-test-files/test_pune.csv \
        --output results_pune.csv
    input: Two strings representing the input_path and output_path.
    output: Writes to the output CSV file and returns nothing.
    error_handling: Safely handle null rows, output a row with flag as "NEEDS_REVIEW", and ensure the batch process does not crash.
