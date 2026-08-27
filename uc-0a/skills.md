# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a specific category, priority level, extraction reason, and review flag based on strict taxonomy rules.
    input: A string representing a single citizen complaint description.
    output: A JSON object containing exactly four keys: 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string or blank).
    error_handling: If the input description is completely unreadable or missing, return 'Other' for category and set the flag to 'NEEDS_REVIEW' with a default 'Low' priority.

  - name: batch_classify
    description: Reads an input CSV file of multiple citizen complaints, applies the classify_complaint skill to each row, and writes the structured results to an output CSV file.
    input: The file path to the input CSV containing citizen complaints (e.g., test_[city].csv).
    output: A generated CSV file (e.g., results_[city].csv) containing the original data appended with the classified columns: category, priority, reason, and flag.
    error_handling: If the input file is missing or formatted incorrectly, log an error immediately and halt execution to prevent silent data corruption.
