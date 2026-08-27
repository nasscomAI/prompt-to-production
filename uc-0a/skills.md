# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Analyzes a single citizen complaint description to determine its category and priority,
      providing a justifying reason and a status flag.
    input: >
      A string containing the raw text of a citizen complaint complaint.
    output: >
      A dictionary or structured object containing:
      - category (string): One of the 10 allowed categories.
      - priority (string): Urgent, Standard, or Low.
      - reason (string): One sentence citing specific words from the description.
      - flag (string): "NEEDS_REVIEW" or blank.
    error_handling: >
      If description is empty or nonsense, output category: Other and flag: NEEDS_REVIEW.
      If category cannot be clearly determined from the taxonomy, use Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads a city-specific CSV file from the input directory, processes each row using
      classify_complaint, and writes the results to a new CSV file in the UC-0A directory.
    input: >
      Path to input file (e.g., ../data/city-test-files/test_pune.csv).
    output: >
      CSV file written to uc-0a/results_[city].csv containing original data plus
      classified category, priority, reason, and flag columns.
    error_handling: >
      Validate input file exists and is readable. If any row fails to classify, skip it
      and log an error, but continue processing the rest of the batch.
