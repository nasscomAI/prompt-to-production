skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category, priority, extracts a reason, and sets a flag if ambiguous.
    input: A single complaint row containing the complaint description.
    output: A JSON object with 'category' (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), 'priority' (Urgent, Standard, Low), 'reason' (one sentence citing specific words), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the category is genuinely ambiguous, set the 'flag' field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: A file path to the input CSV (e.g., ../data/city-test-files/test_[city].csv).
    output: A file path to the output CSV (e.g., uc-0a/results_[city].csv).
    error_handling: If a row cannot be processed, log the error and continue to the next row.
