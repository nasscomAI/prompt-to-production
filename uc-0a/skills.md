skills:
  - name: classify_complaint
    description: Reads one citizen complaint row in and returns the required classification (category, priority, reason, flag).
    input: A single row or text description containing citizen complaint details.
    output: A standardized record with exactly four fields (category, priority, reason, flag).
    error_handling: Outputs category "Other" and flag "NEEDS_REVIEW" logically if the categorization cannot be reliably identified from the text.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill per row, and writes the results to a specified output CSV.
    input: Path to an input CSV file (e.g., `../data/city-test-files/test_[your-city].csv`).
    output: Path to an output CSV file (e.g., `uc-0a/results_[your-city].csv`).
    error_handling: In cases of a row failure, sets flag to "NEEDS_REVIEW" for that row specifically without stopping the overall script execution.
