# skills.md

skills:

* name: classify_complaint
  description: Classifies one citizen complaint into an allowed category and priority, generates a one-sentence evidence-based reason, and flags genuinely ambiguous complaints for review.
  input: One complaint row containing a complaint description as text.
  output: A classification containing category, priority, reason, and flag.
  error_handling: If the complaint is genuinely ambiguous, return category Other and flag NEEDS_REVIEW. If the input is invalid or the complaint description is missing, do not guess and return an appropriate validation error.

* name: batch_classify
  description: Reads complaint rows from an input CSV, applies classify_complaint to every row, and writes the required classification results to an output CSV.
  input: CSV file containing complaint rows with complaint descriptions and without category or priority_flag values.
  output: CSV file containing the original complaint information plus category, priority, reason, and flag fields using the exact required values and format.
  error_handling: Process each valid row independently, do not invent classifications for invalid or genuinely ambiguous complaints, use Other with NEEDS_REVIEW for genuinely ambiguous cases, and report invalid input or processing errors clearly.
