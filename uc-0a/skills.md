# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint description into category, priority, reason, and flag.
    input: dict with key `description` (string, one complaint's free text).
    output: dict with keys `category` (one of the 10 fixed values), `priority` (Urgent/Standard/Low), `reason` (string citing description words), `flag` (NEEDS_REVIEW or empty string).
    error_handling: If description is empty or category cannot be determined, return category=Other, flag=NEEDS_REVIEW, reason explaining why (e.g. "description too vague to classify"). Never raises on ambiguous input — always returns a row.

  - name: batch_classify
    description: Reads the input CSV, runs classify_complaint on every row, writes the output CSV.
    input: `--input` path to test_[city].csv, `--output` path for results_[city].csv.
    output: CSV file at the output path with original columns plus category, priority, reason, flag filled in for every row.
    error_handling: If input file is missing or unreadable, exit with a clear error message and non-zero exit code — do not write a partial output file. If a row is malformed (missing description column), classify_complaint still runs with flag=NEEDS_REVIEW rather than skipping the row.
