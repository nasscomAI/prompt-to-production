# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag.
    input: A dict with keys complaint_id (str) and description (str).
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or None, returns category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a city CSV file and classifies all complaint rows, writing results to a results CSV.
    input: input_path (str) path to test_[city].csv; optional output_path (str) for results CSV.
    output: List of result dicts; also writes results_[city].csv to the same directory as the input.
    error_handling: Raises FileNotFoundError with a clear message if input_path does not exist; skips rows missing both complaint_id and description with a warning.
