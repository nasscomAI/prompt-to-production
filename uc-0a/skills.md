skills:
  - name: [classify_complaint]
    description: [Classifies a single citizen complaint description into a specific category, assigns a priority, and provides a cited justification.]
    input: [type: string format: Unstructured text representing a single citizen complaint description.]
    output: [type: object format: Dictionary containing exactly four fields (category, priority, reason, flag). ]
    error_handling: [Sets the flag to NEEDS_REVIEW when the input is genuinely ambiguous to prevent false confidence, uses the exact allowed list to avoid hallucinated sub-categories, and strictly enforces keyword rules to prevent severity blindness.]

  - name: [batch_classify]
    description: [Reads an input CSV file of complaints, processes each row using the classify_complaint skill, and writes the structured classification results to an output CSV file.]
    input: [type: string format: File path to the input CSV containing citizen complaints. ]
    output: [type: string format: File path to the newly written output CSV with classified data. ]
    error_handling: [Halts or raises an error if outputs exhibit taxonomy drift by using unapproved category variations, and ensures all written rows contain a reason to prevent missing justifications.]
