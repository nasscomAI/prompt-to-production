# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to extract and assign the correct category, priority, reason, and flag.
    input: A string representing a single CSV row of a citizen complaint.
    output: A JSON object with exactly 4 fields (`category`, `priority`, `reason`, `flag`).
    error_handling: If input format is invalid, return generic fallback values with the flag set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV file exactly mapping all the classified rows.
    input: File paths for the input CSV (e.g. `../data/city-test-files/test_[city].csv`).
    output: Writes a structured CSV to `uc-0a/results_[city].csv`. The output CSV must include the newly populated columns for `category`, `priority`, `reason`, and `flag` alongside the original data. Return a success confirmation once the file is generated.
    error_handling: Return a clear error message describing any file reading or writing failures (e.g., File not found, permission denied).
