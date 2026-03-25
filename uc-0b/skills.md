skills:
  - name: retrieve_policy
    description: Load a .txt policy document and return it as structured numbered sections without changing wording.
    input: >
      A file path to a UTF-8 plain-text policy document (for example,
      ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A JSON-like structure with one item per numbered clause: clause_id, raw_text,
      and extracted constraints (actors, approvals, timing, thresholds, exceptions)
      copied from source wording.
    error_handling: >
      If file is missing, unreadable, or has no numbered clauses, return an explicit
      error with reason and do not fabricate sections.

  - name: summarize_policy
    description: Produce a source-faithful summary from structured clauses with clause references and no meaning drift.
    input: >
      Structured numbered sections from retrieve_policy, including clause_id and
      raw_text for each clause.
    output: >
      A clause-referenced summary that covers every numbered clause, preserves all
      conditions and obligations, flags any clause quoted verbatim to prevent
      meaning loss, and includes a clause coverage checklist for 2.3, 2.4, 2.5,
      2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
    error_handling: >
      If any clause is missing, ambiguous, or cannot be summarized without dropping
      conditions, quote that clause verbatim and mark it as 'verbatim to prevent
      meaning loss'; if source structure is invalid, return an explicit error.
