# skills.md — UC-0A Complaint Classifier
skills:
  - name: classify_complaint
    description: Classifies an individual municipal complaint row into a standardized category, priority rating, justification reason, and review flag.
    input: Dictionary representing a single complaint row with keys 'complaint_id', 'date_raised', 'city', 'ward', 'location', 'description', 'reported_by', and 'days_open'.
    output: Dictionary with keys 'complaint_id' (str), 'category' (str), 'priority' (str), 'reason' (str), and 'flag' (str).
    error_handling: When input is malformed, missing required fields, or genuinely ambiguous, assigns category 'Other', evaluates priority against severity keywords, explains the issue in 'reason', and sets 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, iteratively processes each complaint using classify_complaint, and writes the structured classification results to a target CSV file.
    input: input_path (str, path to source CSV file) and output_path (str, path to destination CSV file).
    output: CSV file written to output_path with header columns 'complaint_id,category,priority,reason,flag', and returns summary execution metrics.
    error_handling: Handles missing files or invalid CSV formatting gracefully; isolates individual row parsing errors by outputting fallback review records so batch execution never crashes.
