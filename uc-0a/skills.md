skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row to determine category, priority, reason, and flag based on description text matching.
    input: Dictionary containing the 'description' and 'complaint_id' of the complaint.
    output: Dictionary mapping the classified schema keys (category, priority, reason, flag) to their evaluated string values.
    error_handling: In case of unparseable description or missing values, falls back to 'Other' category and sets 'NEEDS_REVIEW' flag.

  - name: batch_classify
    description: Iterates through all rows of an inputted CSV file and applies classify_complaint on each row safely to output a new CSV file.
    input: String path to the input CSV file and string path to output results CSV file.
    output: A CSV file written to disk containing all rows mapped correctly.
    error_handling: Uses try-except block to gracefully handle failures on individual rows without crashing the batch classification and leaves an error traceback in the reason field and 'NEEDS_REVIEW' flag.
