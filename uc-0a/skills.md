skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into an allowed category and priority with a specific reason and review flag when genuinely ambiguous.
    input: One complaint row containing a description as text.
    output: category, priority, reason, and flag, using only the exact allowed values from the UC-0A schema.
    error_handling: Uses Other and NEEDS_REVIEW when the complaint is genuinely ambiguous, and never invents a category or sub-category.

  - name: batch_classify
    description: Reads a city complaint CSV, classifies every complaint using classify_complaint, and writes the results to an output CSV.
    input: Input CSV file containing complaint rows with descriptions and an output CSV file path.
    output: CSV containing each complaint with category, priority, reason, and flag fields.
    error_handling: Reports invalid or unreadable input instead of silently producing incomplete results, and preserves NEEDS_REVIEW for genuinely ambiguous complaints.