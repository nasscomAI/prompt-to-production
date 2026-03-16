# skills.md

skills:
  - name: classify_complaint
    description: Takes one complaint row in and returns the assigned category, priority, reason, and flag out.
    input: A single complaint row containing a description. Format is typically a row from a CSV or raw text.
    output: category (exact string match), priority (Urgent/Standard/Low), reason (one sentence), flag (NEEDS_REVIEW or blank).
    error_handling: If genuinely ambiguous, output category 'Other' if applicable, and MUST set flag to NEEDS_REVIEW to avoid false confidence.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint per row, and writes the results to an output CSV.
    input: Path to an input CSV file containing unclassified complaint rows.
    output: Path to an output CSV file with classified rows.
    error_handling: If parsing fails or a row cannot be classified, properly flag the row with NEEDS_REVIEW and gracefully continue processing the rest of the CSV.
