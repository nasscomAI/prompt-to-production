skills:
  - name: classify_complaint
    description: Evaluates a single complaint's text to output its classification, priority, and reason.
    input: Dictionary containing a `complaint_id`, `description`, and optionally `location`.
    output: Dictionary with keys `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: If input format is invalid or category is genuinely ambiguous, returns category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a CSV of complaints, classifies each row, and writes the results to a new CSV.
    input: Path to the input CSV file and path to the expected output CSV file.
    output: Creates a new output CSV file with identical input columns plus `category`, `priority`, `reason`, and `flag`.
    error_handling: Catches row-level exceptions to ensure processing continues for subsequent rows.
