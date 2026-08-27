skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint into the correct category,
      priority, reason, and review flag according to the defined schema.
    input: >
      One complaint description (string).
    output: >
      Category, priority, reason, and flag for the complaint.
    error_handling: >
      If the complaint is ambiguous, assign category "Other" and set
      flag to "NEEDS_REVIEW". If the input is empty or invalid,
      return "Other" with "NEEDS_REVIEW".

  - name: batch_classify
    description: >
      Reads an input CSV file, classifies each complaint using
      classify_complaint, and writes the results to an output CSV.
    input: >
      Input CSV file containing complaint descriptions.
    output: >
      Output CSV file with category, priority, reason, and flag columns.
    error_handling: >
      Skip malformed rows where possible. If a row cannot be classified,
      output category "Other" and flag "NEEDS_REVIEW" instead of failing
      the entire batch.