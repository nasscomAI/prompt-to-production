# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Labels one complaint row with an exact category, priority, quoted reason, and optional NEEDS_REVIEW flag.
    input: dict — a single CSV row containing a description field (string)
    output: dict — complaint_id, category, priority, reason, flag
    error_handling: If the description is missing or no category keyword matches, returns category "Other", priority "Standard" (unless a severity keyword is present), a reason explaining the miss, and flag "NEEDS_REVIEW". Never raises on ambiguous or empty input.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to every non-blank row, and writes the results CSV.
    input: input_path (path to test_[city].csv) and output_path (path to results_[city].csv)
    output: writes a CSV with all input columns plus category, priority, reason, flag; prints a summary of row count, Urgent count, NEEDS_REVIEW count, and any invalid categories
    error_handling: A row that raises is emitted as category "Other" with flag "NEEDS_REVIEW" so the batch never crashes; fully blank rows are skipped and counted.
