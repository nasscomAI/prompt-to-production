# skills.md — Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: Loads HR leave policy .txt file, parses numbered clauses, and returns structured sections with clause identifiers and binding verbs.
    input: File path (string) pointing to policy .txt document (e.g., policy_hr_leave.txt).
    output: Dictionary with keys 'clauses' (list of dicts: {clause_id, section, obligation, binding_verb, full_text}) and 'metadata' (source file, format).
    error_handling: If file not found, raise FileNotFoundError with path. If file lacks numbered clauses (e.g., not an HR policy), return error_type='invalid_format' with explanation. If clause structure is incomplete (missing binding_verb), flag with warning.

  - name: summarize_policy
    description: Takes structured policy clauses, produces a concise summary that preserves all obligations and multi-condition requirements without adding unstated context.
    input: Output dict from retrieve_policy (clauses list and metadata).
    output: Dictionary with keys 'summary' (string), 'clause_references' (list of clause_ids included), 'critical_clauses' (list quoted verbatim with flags), 'coverage_score' (0-100 based on clause count), 'condition_audit' (list of multi-condition clauses with preservation status).
    error_handling: If any clause lacks a binding_verb, flag it and include verbatim. If two or more conditions detected in a single clause (e.g., "AND", "both"), validate both are present in summary or mark as "CONDITION_DROP_RISK". If input is malformed or missing required keys, return error_type='invalid_input' with schema details.

