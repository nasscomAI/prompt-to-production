skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on keywords in description, applying RICE taxonomy and priority rules.
    input: dict representing a CSV row, containing 'complaint_id' and 'description'.
    output: dict containing keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is missing or empty, sets category to 'Other', priority to 'Standard', and flags as 'NEEDS_REVIEW'. If multiple categories are matched, chooses a primary and flags as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads complaints from an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: input_path (str) to the source CSV file, output_path (str) to the target results CSV file.
    output: Writes output CSV with columns 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Flags nulls, handles bad rows without crashing, and proceeds to classify remaining rows.
