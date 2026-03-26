skills:

  - name: classify_complaint
  - description: Classifies a single complaint into category, priority, reason, and flag using rule-based logic.
  - input: A dictionary containing at least a "description" field (string).
  - output: A dictionary with keys: complaint_id, category, priority, reason, flag.
  - error_handling: >
  - If description is missing, empty, or invalid, returns category "Other",
  - priority "Low", reason indicating invalid input, and flag "NEEDS_REVIEW".
  - If multiple or no categories match, sets flag to NEEDS_REVIEW.

  - name: batch_classify
  - description: Processes an input CSV of complaints, applies classification row-wise, and writes results to output CSV.
  - input: Input CSV file path with complaint rows.
  - output: Output CSV file with added columns: category, priority, reason, flag.
  - error_handling: >
  - Skips or safely handles malformed rows without crashing.
  - Ensures output file is always generated even if some rows fail.
  - Missing fields are handled with default values and flagged as NEEDS_REVIEW.
