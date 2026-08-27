# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description string to determine its category, priority, reason, and an optional review flag.
    input: A single row containing a citizen complaint string.
    output: Returns category, priority, reason, and flag fields.
    error_handling: If the complaint description is too ambiguous or empty to classify confidently, it falls back to a category of 'Other' and outputs 'NEEDS_REVIEW' in the flag field.

  - name: batch_classify
    description: Reads an input CSV file containing multiple complaint rows, runs classify_complaint on each row, and writes the results to an output CSV file.
    input: Filepath to an input CSV containing complaints (e.g., ../data/city-test-files/test_[city].csv).
    output: A completed CSV file summarizing the processed classifications (e.g., uc-0a/results_[city].csv).
    error_handling: If a row fails to process during batch classification, logs the failure and proceeds to the next row to guarantee the generation of the output file.
