skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and classifies it into a predefined category, priority, reason, and flag according to the UC-0A rules.
    input: A single text string containing the citizen's complaint description.
    output: A structured object containing category (string), priority (string), reason (string), and flag (string or blank).
    error_handling: If the category cannot be confidently determined or is genuinely ambiguous, it sets the flag to 'NEEDS_REVIEW'. If the input is empty or invalid, it returns a default error classification.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: A path to the input CSV file containing citizen complaints, and a path for the output CSV.
    output: A generated output CSV file containing the classification columns (category, priority, reason, flag) added for each row.
    error_handling: Skips or logs rows with malformed input data while continuing to process the rest of the batch. Handles missing input files gracefully by raising an appropriate FileNotFoundError.
