skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to determine its category, priority level, and justification based on a specific urban infrastructure schema.
    input:
      type: object
      format: A dictionary or single row containing a text description of the complaint.
    output:
      type: object
      format: A structured record containing category, priority, reason (one sentence citing keywords), and flag (NEEDS_REVIEW or blank).
    error_handling: Returns NEEDS_REVIEW in the flag field if the category is ambiguous; forces Urgent priority if severity keywords are detected; rejects any category not present in the strict allowed list to prevent taxonomy drift.
  - name: batch_classify
    description: Orchestrates the end-to-end processing of a city-specific CSV file by applying individual classification logic to every row and saving the results.
    input:
      type: file
      format: CSV file located at ../data/city-test-files/test_[your-city].csv containing 15 complaint rows.
    output:
      type: file
      format: CSV file located at uc-0a/results_[your-city].csv with populated classification columns.
    error_handling: Validates input file existence and format; logs instances of severity blindness or schema violations; ensures consistent category naming across the entire batch to prevent hallucinated sub-categories.