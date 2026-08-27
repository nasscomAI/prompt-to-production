# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, and reasoning based on literal evidence and safety keywords.
    input: A single complaint description string.
    output: A structured object containing: `category` (Exact string from allowed list), `priority` (Urgent/Standard/Low), `reason` (One sentence citing description), and `flag` (NEEDS_REVIEW or blank).
    error_handling: For ambiguous or unknown issues, sets `category` to 'Other' and `flag` to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an input CSV file of citizen complaints, applying `classify_complaint` to each row and writing the results to a structured output CSV.
    input: Absolute or relative path to a city-specific CSV file (`../data/city-test-files/test_[your-city].csv`).
    output: Absolute or relative path to the generated results CSV (`uc-0a/results_[your-city].csv`).
    error_handling: Logs warnings for rows with missing descriptions and proceeds with the rest of the batch; sets `category` to 'Other' if a row fails standard classification.
