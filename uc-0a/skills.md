# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint record into an exact category and priority, accompanied by an evidence-backed reason and ambiguity flag.
    input: dict containing complaint row fields (`complaint_id`, `date_raised`, `city`, `ward`, `location`, `description`, `reported_by`, `days_open`).
    output: dict containing exact keys `{complaint_id, category, priority, reason, flag}` where category is in the allowed taxonomy and priority reflects severity keywords.
    error_handling: When description is missing, empty, or genuinely ambiguous, set `category: Other`, `priority: Standard` (or `Urgent` if severity keywords are matched), `flag: NEEDS_REVIEW`, and state the missing details or ambiguity in `reason`.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, iteratively executes `classify_complaint` for each row, and writes the structured classification results to a target CSV file.
    input: `input_path` (str, path to input CSV file) and `output_path` (str, path to write output CSV file).
    output: CSV file at `output_path` containing columns `complaint_id,category,priority,reason,flag`.
    error_handling: Handles file reading/writing errors and malformed or null rows gracefully without terminating the execution; flags problematic entries with `NEEDS_REVIEW` and ensures valid rows are fully written.
