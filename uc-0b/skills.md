# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns content as structured numbered sections with clause references.
    input: "File path to policy document (.txt)"
    output: "Dict with keys: clauses (list of dicts with 'number', 'text', 'section' keys), metadata (dict with filename, word_count)"
    error_handling: "If file not found, raise FileNotFoundError. If file empty, return empty clauses list. If malformed (unreadable encoding), log error and attempt UTF-8 recovery."

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with all clauses preserved and clause references, detecting and flagging clause omission and multi-condition drops.
    input: "Dict returned from retrieve_policy (clauses list with number, text, section)"
    output: "String: formatted summary with clause numbers, core obligations, binding verbs preserved, [VERBATIM] markers where needed, and end metadata showing clause count verification"
    error_handling: "If input lacks required keys, raise KeyError. If summary would omit clause, add [CLAUSE_CHECK] marker. If multi-condition requirement detected but conditions appear incomplete, flag with [MULTI-CONDITION] marker for manual review."
