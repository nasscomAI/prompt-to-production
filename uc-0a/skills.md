skills:
  - name: classify_complaint
    description: Analyzes the text description of a single municipal complaint row and outputs its category, priority, reason, and review flag.
    input: A dictionary representing a single CSV row with keys like 'description' and 'complaint_id'.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Flags missing values or ambiguous descriptions with 'NEEDS_REVIEW' and defaults category to 'Other'.

  - name: batch_classify
    description: Reads complaints from an input CSV, runs single-row classification on each, and writes the results to an output CSV.
    input: Input CSV file path containing raw complaints and output CSV file path where results will be stored.
    output: A generated CSV file containing classified complaints.
    error_handling: Catches and logs row-level exceptions, skips or gracefully handles bad data formats, and guarantees an output file is generated even if specific rows fail.
