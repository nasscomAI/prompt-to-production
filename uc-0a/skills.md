# skills.md
# UC-0A Complaint Classifier skills definition.

skills:
  - name: classify_complaint
    description: Classify one complaint row into UC-0A output fields using only the provided complaint text and metadata.
    input: dict representing a CSV row, including fields such as complaint_id, description, complaint, text, and other metadata.
    output: dict with keys category, priority, reason, and flag.
    error_handling: If the complaint description is missing or ambiguous, return category Other or the closest allowed category, set flag to NEEDS_REVIEW, and provide a reason citing available description text.

  - name: batch_classify
    description: Read an input CSV file, apply classify_complaint to each row, and write a results CSV with classification fields.
    input: input CSV file path with complaint rows.
    output: output CSV file path containing columns complaint_id, category, priority, reason, and flag.
    error_handling: Continue processing all rows even if some fail; for rows that cannot be classified, write category Other, priority Low, flag NEEDS_REVIEW, and a reason explaining the failure.

allowed_categories:
  - Water Supply
  - Road Repair
  - Street Light
  - Sanitation

priority_rules:
  - Urgent if the complaint mentions children or injuries.
  - Otherwise Standard or Low based on severity and context.
