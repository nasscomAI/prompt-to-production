skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category, priority, and justification based on a strict taxonomy and keyword-based severity rules.
    input: String (A text description of the complaint)
    output: Dictionary/JSON containing category, priority, reason, and flag
    error_handling: If the description is empty or too short, returns category 'Other' with the 'NEEDS_REVIEW' flag. If the category is ambiguous, it uses 'Other' and flags for review rather than guessing.

  - name: batch_classify
    description: Automates the processing of multiple complaints from an input CSV file and writes the classified results to a new CSV file.
    input: Path to Input CSV (test_[your-city].csv) and Path to Output CSV (results_[your-city].csv)
    output: Status message indicating the number of rows processed and the location of the result file.
    error_handling: Validates that the input file exists and has the required columns; reports rows that failed processing and continues with the rest of the file.
