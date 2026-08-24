skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint record into standard category, priority level, justification reason, and review flag based on strict enforcement rules.
    input: A dictionary containing complaint record fields (complaint_id, description, location, ward, etc.).
    output: A dictionary with keys {complaint_id, category, priority, reason, flag}.
    error_handling: If description is missing, empty, or unclassifiable, sets category to 'Other', priority to 'Standard', reason citing missing/ambiguous details, and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of citizen complaints, iteratively runs classify_complaint on each row, and writes the structured classification results to a target output CSV.
    input: input_path (str path to input CSV) and output_path (str path to destination CSV).
    output: Writes output CSV containing columns [complaint_id, category, priority, reason, flag] and returns summary statistics or status.
    error_handling: Handles malformed rows and missing fields gracefully without crashing, logging error rows and assigning default fallback values with flag 'NEEDS_REVIEW'.
