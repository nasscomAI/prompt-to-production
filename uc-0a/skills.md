# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single raw complaint row into the city governance taxonomy.
    input: A dictionary containing at least a 'description' field and 'complaint_id'.
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If input is missing or description is null, return category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying classify_complaint to each row and saving results.
    input: File paths for input CSV and output CSV.
    output: None (writes results to CSV).
    error_handling: Skip malformed CSV rows; ensure the process continues even if individual row classification fails. Apply 'NEEDS_REVIEW' flag for ambiguous data.
