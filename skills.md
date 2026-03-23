# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on RICE enforcement rules.
    input: CSV row with fields (description). Type: string. Format: plain text complaint description from citizen input.
    output: JSON object with fields {category, priority, reason, flag}. Category is one of the 10 allowed types, priority is Urgent/Standard/Low, reason is a single sentence citing the description, flag is NEEDS_REVIEW or empty.
    error_handling: If description is empty or ambiguous, classify as Other with flag NEEDS_REVIEW. If severity keywords are present, force priority to Urgent. If reason cannot cite specific words from description, return error indicating incomplete input.

  - name: batch_classify
    description: Reads input CSV file, applies classify_complaint to each row, writes results to output CSV with consistent schema.
    input: CSV file path with columns (id, description, ...). Type: file path. Format: standard UTF-8 CSV with header row.
    output: CSV file with columns (id, category, priority, reason, flag). Type: file. Format: standard UTF-8 CSV, one result row per input row.
    error_handling: If input file is malformed, skip rows with errors and log to stderr. If output directory does not exist, create it. If duplicate IDs are encountered, process all rows but warn in logs.