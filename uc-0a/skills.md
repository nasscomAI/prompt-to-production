skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into category + priority + reason + flag using the fixed taxonomy and severity rules.
    input: A dict with at least a "description" key (string) and a "complaint_id" key.
    output: A dict with keys complaint_id, category, priority, reason, flag. category is always one of the 10 allowed strings; priority is Urgent/Standard/Low; flag is NEEDS_REVIEW or "".
    error_handling: When no keyword matches the description, returns category "Other" with flag NEEDS_REVIEW. When two or more categories are meaningfully present, returns the highest-scoring category with flag NEEDS_REVIEW. Raises no exception for ambiguous input.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (path to test_[city].csv) and output_path (path to write results_[city].csv).
    output: Writes results_[city].csv with header complaint_id, category, priority, reason, flag; one row per input row; prints summary counts to stdout.
    error_handling: Missing input file or empty input prints an error to stderr and exits with status 1. A malformed row is classified as category Other with flag NEEDS_REVIEW instead of crashing; the output file is always produced even if some rows fail.