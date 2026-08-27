# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: "File path (string): path to policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)"
    output: "Structured dict/object with keys: raw_content (full text), sections (list of numbered clauses with clause_id, text, binding_verb extracted)"
    error_handling: "If file does not exist, returns error object {error: 'FILE_NOT_FOUND', path: <requested_path>}. If file is corrupted or unreadable, returns {error: 'FILE_UNREADABLE', details: <reason>}. If document does not contain expected numbered clause structure, logs warning but returns available content."

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with all clause references, obligations, and conditions preserved.
    input: "Object: {sections: [list of clause objects from retrieve_policy], enforcement_mode: 'strict' (default) | 'permissive'}"
    output: "Object: {summary: <text>, clause_count: <int>, missing_clauses: [list of clause_ids], flagged_clauses: [list of {clause_id, reason, verbatim_quote}], warnings: [list of detected scope_bleed or condition_drops]}"
    error_handling: "If input sections array is empty, returns {error: 'NO_CLAUSES_PROVIDED'}. If enforcement_mode is 'strict' and any clause is missing or conditions dropped, returns error with details rather than incomplete summary. If text cannot be summarised without semantic loss, flags clause and includes verbatim quote in output."
