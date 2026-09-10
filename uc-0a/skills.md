skills:
  - name: classify_complaint
    description: Classifies one citizen complaint according to the UC-0A classification schema.
    input: One complaint row containing the supplied complaint information, including its description.
    output: category, priority, reason, and flag, using only the values and rules defined by UC-0A.
    error_handling: If the category is genuinely ambiguous, return category Other and flag NEEDS_REVIEW. If a mandatory severity keyword is present, priority must be Urgent.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each complaint row, and writes the classification results to an output CSV.
    input: An input CSV containing the supplied citizen complaint rows.
    output: An output CSV containing the classification results for each complaint.
    error_handling: Apply the UC-0A classification and ambiguity rules consistently to each complaint row.