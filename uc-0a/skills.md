skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine category, priority, reason, and flag.
    input: A single complaint record string (e.g., from a CSV row) containing the raw text description.
    output: A structured object containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If description is empty or missing, classify as "Other", priority "Low", flag "NEEDS_REVIEW". If ambiguous, set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, calls `classify_complaint` for each row, and writes the results to an output CSV.
    input: Input CSV file path (e.g., test_[city].csv) and output CSV file path.
    output: A complete, properly classified CSV written to the output path.
    error_handling: If the input file is missing, abort. If a single row fails processing, record it as failed but continue processing remaining rows.
