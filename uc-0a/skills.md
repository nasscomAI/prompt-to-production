skills:
  - name: classify_complaint
    description: Classify one civic complaint using the fixed taxonomy, severity rules, evidence-based reason, and ambiguity flag.
    input: One CSV complaint row containing complaint_id, location, and description.
    output: complaint_id, category, priority, reason, and flag.
    error_handling: Return Other, Low, and NEEDS_REVIEW when the description is missing or genuinely ambiguous; never invent facts.

  - name: batch_classify
    description: Read a complaint CSV, classify every row independently, and write a results CSV.
    input: Input CSV path and output CSV path.
    output: One result row per input complaint, including malformed-row handling.
    error_handling: Do not crash on missing fields or bad rows; preserve the complaint_id when available and flag rows needing review.
