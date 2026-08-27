skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint description into category, priority, reason, and flag according to the defined schema.
    input: A single complaint description string from the CSV row.
    output: category (string), priority (string), reason (one sentence referencing words from the complaint), flag (blank or NEEDS_REVIEW).
    error_handling: If the complaint cannot be confidently classified using the allowed categories, return category as "Other" and set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes a CSV file of complaints and applies classify_complaint to each row.
    input: CSV file containing complaint descriptions.
    output: CSV file with columns category, priority, reason, and flag for each complaint row.
    error_handling: If an input row is empty or malformed, skip the row or mark it as category "Other" with flag "NEEDS_REVIEW".