skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint into an allowed taxonomy category, assigns an urgency priority based on severity keywords, produces a one-sentence evidence reason, and sets an ambiguity review flag.
    input: Dictionary representing a single complaint record containing at least 'complaint_id' (string) and 'description' (string).
    output: Dictionary with exact keys 'complaint_id' (string), 'category' (string from allowed taxonomy), 'priority' (Urgent | Standard | Low), 'reason' (string, single sentence citing words from text), and 'flag' (NEEDS_REVIEW or empty string).
    error_handling: If description is missing or null, returns category 'Other', priority 'Low', reason 'Missing description in input record.', and flag 'NEEDS_REVIEW'. If ambiguous or contradictory, assigns closest category and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Iterates through an input CSV of citizen complaints, executes classify_complaint for each row without crashing on malformed entries, and persists the standardized results into an output CSV.
    input: Two file paths as strings: 'input_path' (pointing to an existing test_[city].csv) and 'output_path' (destination results_[city].csv).
    output: Writes a UTF-8 CSV file to 'output_path' with column headers complaint_id, category, priority, reason, flag, and returns None.
    error_handling: Handles missing input file with FileNotFoundError; for malformed or unparseable individual rows, catches exceptions, creates a fallback record with flag 'NEEDS_REVIEW', and continues processing subsequent rows to ensure non-empty output generation.