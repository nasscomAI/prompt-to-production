skills:
  - name: classify_complaint
    description: Analyzes a single municipal complaint row to determine category, priority, and justification.
    input: Dictionary containing 'complaint_id', 'description', and metadata (city, ward, location).
    output: Dictionary with 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is missing, set category to 'Other', priority to 'Low', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a CSV file of complaints from 'data/city-test-files', applying classify_complaint to each row and generating a results CSV inside the 'uc-0a' folder.
    input: Path to input CSV in 'data/city-test-files' and Path to output CSV in 'uc-0a'.
    output: A CSV file in the 'uc-0a' directory named 'results_[city].csv'.
    error_handling: Must flag nulls in output, handle malformed CSV rows without crashing, and ensure every valid row is processed.


