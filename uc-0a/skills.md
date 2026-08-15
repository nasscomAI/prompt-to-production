# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into the fixed schema (category, priority, reason, flag).
    input: One complaint row as a dict with a non-empty 'description' string; complaint_id, ward, and location are optional but preserved for traceability.
    output: A dict with exactly the keys category, priority, reason, flag, using only the allowed schema values.
    error_handling: Returns category=Other, priority=Standard, flag=NEEDS_REVIEW, and a reason explaining the problem when the description is missing, empty, matches no category, or matches more than one category.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to every row, and writes a results CSV with the classification columns appended.
    input: input_path pointing at ../data/city-test-files/test_[city].csv and output_path for the results file.
    output: Writes a CSV containing every original column plus category, priority, reason, flag, with one row per input row.
    error_handling: Never crashes on a bad row — a failed row is still written with category=Other and flag=NEEDS_REVIEW while remaining rows are classified; raises only if the input file cannot be opened or has no header row.
