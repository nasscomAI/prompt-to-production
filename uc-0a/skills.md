skills:
  - name: classify_complaint
    description: Parses a single input row to select taxonomy category, identify severity keywords, and determine review status.
    input: Dictionary row containing key 'description'.
    output: Dict structure with keys: complaint_id, category, priority, reason, flag.
    error_handling: Handles null strings safely by setting flag to 'NEEDS_REVIEW' and category to 'Other'.

  - name: batch_classify
    description: Runs the file streaming engine that parses the incoming records and exports structured telemetry logs.
    input: Path strings pointing to raw data sources and target write destinations.
    output: Void. Emits classified dataset to specified output location.
    error_handling: Continues processing remaining entries if a specific row encounters an execution error.