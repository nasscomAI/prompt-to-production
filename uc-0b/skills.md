skills:
  - name: retrieve_policy
    description: Load a `.txt` HR policy document and return structured numbered sections and clauses.
    input: >
      object with `file_path` (string, required) pointing to a plain-text policy
      file, optionally `document_id` (string).
    output: >
      object with `document_id`, `title`, and `sections` array where each section
      has `section_number`, `section_title`, and `clauses` array; each clause has
      `clause_id` (for example `2.3`) and `clause_text`.
    error_handling: >
      Return a validation error when file is missing, unreadable, non-text, or
      has no parseable numbered clauses; do not infer missing section numbers.

  - name: summarize_policy
    description: Produce a compliant summary from structured clauses with explicit clause references.
    input: >
      object containing `sections` from `retrieve_policy` output and optional
      `focus_clauses` array; input must preserve clause IDs.
    output: >
      object with `summary_items` array; each item includes `summary_text`,
      `source_clauses` (array of clause IDs), and optional `verbatim` flag for
      clauses quoted to avoid meaning loss.
    error_handling: >
      Reject output generation if any clause is missing, any multi-condition
      obligation is partially represented, or unsupported text is introduced.
      When compression risks meaning loss, quote the original clause verbatim and
      flag it instead of guessing.
