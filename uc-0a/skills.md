# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into its appropriate category, priority, reason, and review flag.
    input: A string containing exactly one citizen complaint description to be classified.
    output: A structured object containing four fields: category (from the 10 allowed values), priority (Urgent, Standard, or Low), reason (a sentence citing specific words), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is ambiguous or category cannot be derived confidently, assigns category "Other" and flag "NEEDS_REVIEW". If input is completely unparseable, returns a structured error.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV file, applies the classify_complaint skill to each row, and writes the results to an output CSV file.
    input: The file path to the input CSV containing citizen complaints (e.g., ../data/city-test-files/test_[city].csv).
    output: The file path to the generated output CSV file containing the classification results (e.g., uc-0a/results_[city].csv).
    error_handling: Halts execution and throws an error if the input file is missing or unreadable. If an individual row fails to classify, updates the row with the NEEDS_REVIEW flag and continues processing to the next row.
