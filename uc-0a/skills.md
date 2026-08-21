skills:
  - name: classify_complaint
    description: >
      Classify a single municipal complaint record into the required category,
      priority, reason, and flag fields using the UC-0A specification.
    inputs:
      - complaint record containing description, location, and ward
    outputs:
      - category
      - priority
      - reason
      - flag
    rules:
      - Use only the allowed 10-category taxonomy.
      - Set priority to Urgent when the description contains a required severity keyword.
      - Otherwise assign Standard or Low according to the complaint context.
      - Generate a single-sentence reason grounded in specific words from the description.
      - If the category is ambiguous or cannot be determined with confidence, use Other and NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read complaint records from a CSV file, classify each record using
      classify_complaint, and write the classification results to an output CSV.
    inputs:
      - input CSV path
      - output CSV path
    outputs:
      - CSV containing the original complaint fields and classification fields
    rules:
      - Process each complaint independently.
      - Preserve the required input fields.
      - Add category, priority, reason, and flag fields.
      - Handle missing or malformed complaint records without terminating the entire batch.
      - Ensure every output category belongs to the allowed taxonomy.