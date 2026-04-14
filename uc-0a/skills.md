# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority level, justification, and ambiguity flag.
    input: A dictionary or object containing the complaint 'description'.
    output: A dictionary with 'category', 'priority', 'reason', and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the description is too short to classify or highly ambiguous, return category 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a city's test files, reading from an input CSV and writing to a results CSV.
    input: Path to the input CSV file (e.g., test_pune.csv) and the desired output CSV path.
    output: A generated CSV file located at uc-0a/results_[city].csv containing the classified data.
    error_handling: If the input file is missing, the skill logs a fatal error. If individual rows fail classification, they are flagged for review rather than stopping the process.
