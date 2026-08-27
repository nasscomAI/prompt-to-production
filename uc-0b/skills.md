skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections for downstream validation and summarization.
    input: "Object with file_path: string ending in .txt, encoded as UTF-8 text."
    output: "Object with sections: array of {clause_id: string, text: string}, plus raw_text: string."
    error_handling: "Returns an error if file is missing, unreadable, non-.txt, empty, or if numbered clauses cannot be reliably parsed."

  - name: summarize_policy
    description: Produces a compliant policy summary from structured sections while preserving clause meaning and all mandatory conditions.
    input: "Object with sections from retrieve_policy and required_clause_ids: [2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2]."
    output: "Object with summary_text: string, included_clause_ids: string[], and quoted_clauses: string[] when verbatim retention is required."
    error_handling: "Returns a validation error if any required clause is missing, if any multi-condition obligation is partially represented, or if unsupported text is introduced."
