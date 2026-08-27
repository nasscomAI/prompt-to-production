skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag
    input: dict - a single CSV row as dictionary with complaint_id, description, etc.
    output: dict - with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is missing or processing fails, return Other category with NEEDS_REVIEW flag

  - name: batch_classify
    description: Reads input CSV, classifies each row, writes results to output CSV
    input: str, str - input CSV file path and output CSV file path
    output: None - writes results to output file
    error_handling: If input file cannot be read, create empty output; if individual row fails, log error and continue with next row