skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, and reason, with review flagging for ambiguous complaints.
    input: Dictionary representing a CSV row with keys like 'complaint_id', 'date_raised', 'city', 'ward', 'location', 'description', etc.
    output: Dictionary containing keys: 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If the complaint description is empty or missing, defaults the category to 'Other', priority to 'Low', reason to 'Empty complaint description', and sets the flag to 'NEEDS_REVIEW'. If multiple category patterns match or none match, sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads the input CSV containing citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Paths to input CSV file and output CSV file.
    output: Writes a CSV file containing columns: 'complaint_id', 'category', 'priority', 'reason', 'flag' and returns None.
    error_handling: Flags empty descriptions or missing values, logs row-level errors without crashing, and ensures the output file is created even if some rows are problematic.
