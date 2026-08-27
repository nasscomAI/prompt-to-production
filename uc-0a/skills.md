# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint text to assign an exact category, priority, one-sentence justification, and optional review flag.
    input: A single string containing the complaint description.
    output: A structure containing 4 classified fields (category, priority, reason, flag) matching strictly to constraints.
    error_handling: If the complaint description is ambiguous and category cannot be determined definitively, set the `flag` field to `NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies `classify_complaint` to each row, and writes the structured outputs to a new CSV file.
    input: File path to the input CSV (e.g., `../data/city-test-files/test_[your-city].csv`).
    output: A newly written output CSV file containing the classifications (e.g., `uc-0a/results_[your-city].csv`).
    error_handling: If the input file is missing or invalid, generate an error. If a single row fails, log the error for that row and continue processing remaining rows.
