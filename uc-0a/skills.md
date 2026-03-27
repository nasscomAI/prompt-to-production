skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category and priority based on strict keyword matching.
    input: A dictionary or string representing a single row from the citizen complaint dataset.
    output: A tuple or dictionary containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty or the category is ambiguous, it assigns 'Other' and sets the flag to 'NEEDS_REVIEW'.


  - name: batch_classify
    description: Orchestrates the end-to-end processing of a CSV file by iterating through rows and saving the enriched results to a new file.
    input: File paths for the input CSV (test data) and the desired output CSV location.
    output: A physical CSV file containing the original data plus four new classification columns.
    error_handling: Validates the existence of the input file path; if the file is missing, it logs an error and terminates the process without crashing.
