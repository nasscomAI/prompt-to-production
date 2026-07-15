# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into the required schema.
    input: A single complaint row dictionary with a description field.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is too ambiguous, return category Other and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read a CSV of complaints and write a classification CSV with one row per complaint.
    input: An input CSV path and an output CSV path.
    output: A written CSV file containing the classification results.
    error_handling: If a row fails classification, write a safe fallback row with category Other and flag NEEDS_REVIEW.
