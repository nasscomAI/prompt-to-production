skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on its description into category, priority, reason, and review flag.
    input: A dictionary representing a single CSV row with keys like 'complaint_id' and 'description'.
    output: A dictionary containing the keys: 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If critical inputs are missing or description is empty, categorizes as 'Other' and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a CSV file of complaints, classifies each row, and writes the results to an output CSV.
    input: Paths to input and output CSV files.
    output: Writes output CSV containing the columns: 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Flags rows with null/missing values, handles parsing errors gracefully without crashing the whole batch run, and produces output even if some rows fail.
