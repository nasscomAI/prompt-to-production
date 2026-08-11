skills:
  - name: [classify_complaint]
    description: [Classify one citizen complaint into an allowed category and priority, provide a one-sentence reason, and set a review flag when the category is genuinely ambiguous]
    input: [One complaint row from the input CSV containing a complaint_id and complaint description.]
    output: [ A classification record containing complaint_id, category, priority, reason, and flag using only the allowed values defined by UC-0A.]
    error_handling: [If the description is missing or cannot be reliably classified, use category Other and flag NEEDS_REVIEW; never invent a category or priority.]

  - name: [batch_classify]
    description: [Read the input CSV, classify every complaint using classify_complaint, and write the classification results to an output CSV.]
    input: [A CSV file containing citizen complaint rows.]
    output: [A CSV containing complaint_id, category, priority, reason, and flag for every input row.]
    error_handling: [Handle missing or malformed rows without crashing the entire batch; produce an output record for failed or ambiguous rows using Other and NEEDS_REVIEW where appropriate.]
