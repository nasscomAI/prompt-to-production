skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and extracts classification details including category, priority, reason, and review flag.
    input: A single citizen complaint row containing the description.
    output: A record containing exact values for category, priority, reason, and flag.
    error_handling: Return category as 'Other' and flag as 'NEEDS_REVIEW' if the classification is ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of complaints, processes each row using classify_complaint, and writes the results to an output CSV.
    input: Path to the input CSV file (e.g., ../data/city-test-files/test_[city].csv).
    output: Generates a CSV file (e.g., results_[city].csv) with classified data.
    error_handling: If a row is malformed, skip it and log the error, continuing with the rest of the complaints in the CSV.
