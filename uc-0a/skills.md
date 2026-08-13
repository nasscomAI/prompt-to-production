# skills.md — UC-0A Skills

skills:
  - name: classify_complaint
    description: Receives a single complaint row dictionary, extracts semantic tags, applies deterministic mapping rules, checks for safety/severity keywords, and returns classified category, priority, grounded reason, and review flags.
    input: dict containing "complaint_id", "description", "days_open", and other original columns.
    output: dict containing keys: "complaint_id", "category", "priority", "reason", "flag".
    error_handling: Falls back to "Other" category and flags as "NEEDS_REVIEW" if description is missing or invalid.

  - name: batch_classify
    description: Reads a CSV of citizen complaints, iterates over each row, invokes the classify_complaint skill, and writes a standard results CSV without crashing on corrupted or empty rows.
    input: Path to input CSV file and target path to output CSV file.
    output: Writes output CSV containing the standard classification schema columns.
    error_handling: Catches internal processing exceptions per row, generating a "NEEDS_REVIEW" placeholder row to guarantee output completion.
