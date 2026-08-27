# skills.md
skills:
  - name: classify_complaint
    description: Classifies a single complaint row into an exact category, priority, reason, and ambiguity flag.
    input: A single row as a dict, minimally containing `complaint_id` and `description`.
    output: A dict with keys `complaint_id`, `category`, `priority`, `reason`, `flag`.
    error_handling: When the description is missing, unparseable, or the category is genuinely ambiguous, returns category "Other" with flag "NEEDS_REVIEW" and a reason explaining why, instead of raising.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes the results CSV.
    input: Path to a CSV file (e.g. ../data/city-test-files/test_pune.csv).
    output: A results CSV with one row per input row, carrying the original columns plus category, priority, reason, flag.
    error_handling: Never crashes on a bad row; failed rows are written as a best-effort row with flag NEEDS_REVIEW and a reason noting the failure, so the output is produced even if some rows fail.
