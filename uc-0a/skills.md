skills:

* name: classify_complaint
  description: Classifies a single complaint into category and priority.
  input: A dictionary representing one row from the complaint CSV file.
  output: Dictionary with complaint_id, category, priority, reason, and flag.
  error_handling: If category cannot be determined, return category "Other" and set flag "NEEDS_REVIEW".

* name: batch_classify
  description: Processes all complaints from an input CSV file and writes classified results to a new CSV.
  input: Input CSV path containing complaint rows.
  output: Output CSV file with classification results for each complaint.
  error_handling: Skip invalid rows, flag missing descriptions, and continue processing remaining rows.
