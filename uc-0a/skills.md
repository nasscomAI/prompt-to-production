# skills.md

skills:

- name: classify_complaint
  description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description.
  input: A dictionary representing a CSV row with at least a 'description' key containing the complaint text.
  output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
  error_handling: If description is missing or empty, return category 'Other', priority 'Low', reason 'No description provided', flag 'NEEDS_REVIEW'.

- name: batch_classify
  description: Processes a CSV file of complaints, classifies each row using classify_complaint, and writes the results to a new CSV.
  input: File paths for input CSV and output CSV.
  output: Writes a CSV file with classified results; returns nothing but prints completion message.
  error_handling: Skips rows with invalid data, logs errors, but continues processing; ensures output file is created even if some rows fail.
