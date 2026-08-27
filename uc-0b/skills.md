# skills.md

skills:
  - name: retrieve_policy
    description: Load .txt policy file and return content as structured numbered sections with clause markers.
    input: File path (string) pointing to HR leave policy .txt file.
    output: Dictionary with keys 'sections' (list of {"clause_id": "2.3", "text": "clause text"}) and 'raw' (full file text).
    error_handling: Return error code 'FILE_NOT_FOUND' if path invalid. Return 'NOT_POLICY_FORMAT' if no numbered sections detected (must have pattern X.Y).

  - name: summarize_policy
    description: Consume structured policy sections and produce summary preserving all clauses, conditions, and binding obligations without scope drift.
    input: Structured output from retrieve_policy (sections list + raw text).
    output: Summary text with inline clause references [X.Y] and mapping table listing clause_id → summary_line. Flag any [MEANING-CRITICAL] clauses requiring verbatim quotation.
    error_handling: If <1 sections found, return 'NO_CLAUSES_DETECTED'. If summary would drop detected conditions (via semantic comparison), return 'CONDITION_LOSS_DETECTED: [clause_id] lost condition [condition_text]'.
