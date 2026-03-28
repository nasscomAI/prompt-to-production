# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using the strict UC-0A schema.
    input: dict with keys including complaint_id and description (text), plus any other metadata fields.
    output: dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is missing, invalid, or ambiguous, set category to Other, priority to Low (or Urgent if severity keyword present), reason to a one-sentence fallback citing any available words, and flag to NEEDS_REVIEW for ambiguity or schema failure.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: input_path string (CSV file path), output_path string (destination CSV path).
    output: CSV file at output_path with columns complaint_id, category, priority, reason, flag.
    error_handling: Continues on row-level errors; for failed rows, writes fallback row with category Other, priority Low, reason indicating failure, and flag NEEDS_REVIEW, while processing remaining rows.

