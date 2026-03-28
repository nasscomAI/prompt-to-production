skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to ascertain its standardized category, priority, reason, and review flag.
    input: String representing a single citizen complaint description.
    output: Structured object with exactly four fields (category, priority, reason, flag).
    error_handling: Sets the flag to NEEDS_REVIEW for genuinely ambiguous complaints to prevent false confidence; restricts output strictly to the allowed list to prevent taxonomy drift and hallucinated sub-categories; elevates priority to Urgent upon encountering severity keywords to prevent severity blindness; and fails or retries if the required one-sentence justification is missing.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the classified records to an output CSV.
    input: String representing the file path to an input CSV.
    output: String representing the file path to the generated output CSV.
    error_handling: Halts processing with a prominent error if the input file is inaccessible or malformed, and safely logs and skips individual unprocessable rows to ensure batch completion.
