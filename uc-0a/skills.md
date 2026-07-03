skills:
  - name: classify_complaint
    description: Classifies a single complaint description into standard category, priority, and reason with review flag.
    input: A dictionary representing one complaint row with 'complaint_id' and 'description'.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is missing or invalid, category is set to 'Other', priority is set to 'Standard', and flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads complaints from an input CSV file, runs classify_complaint on each row, and writes results to an output CSV file.
    input: Paths to the input CSV and output CSV files.
    output: Creates the output CSV file and returns the count of processed rows.
    error_handling: Catches individual row errors without crashing, reporting any problematic rows to stdout.
