# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row to extract and classify its information.
    input: One complaint row (text description) from the input CSV.
    output: A categorized object with `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the complaint is ambiguous or the category cannot be confidently determined, outputs category as "Other" and sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Input CSV file path (e.g., ../data/city-test-files/test_[city].csv).
    output: Output CSV file path (e.g., uc-0a/results_[city].csv).
    error_handling: If a row fails processing or is malformed, logs the error for that row and continues processing remaining rows without halting the process.
