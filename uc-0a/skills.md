
skills:
  - name: classify_complaint
    description: Classifies a single civic complaint into one allowed category, one priority level, a short reason, and an optional review flag.
    input: A single complaint record from the input CSV, provided as a structured row/object containing the complaint description and any available row fields.
    output: A structured row/object with category, priority, reason, and flag fields appended to the original complaint record.
    error_handling: If the complaint text is missing, unclear, or strongly matches multiple categories, return category as Other and set flag as NEEDS_REVIEW instead of guessing.

  - name: validate_classification
    description: Verifies that the generated complaint classification follows the required taxonomy and urgency rules before output is written.
    input: A structured classification result containing category, priority, reason, flag, and the original complaint description.
    output: A validated structured classification result that is safe to write to the results CSV.
    error_handling: If category is outside the allowed taxonomy, reason is missing, or urgency rules are violated, correct the output when safely possible; otherwise downgrade to category Other and set flag as NEEDS_REVIEW.