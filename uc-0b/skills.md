# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: file_path (str) — path to a policy .txt file.
    output: A dictionary mapping clause numbers (str) to clause text (str), plus a 'full_text' key with the complete document content.
    error_handling: If file is missing, raise FileNotFoundError. If file is empty, return empty dictionary with a warning. If clauses are unnumbered, return full_text only with a warning about missing clause structure.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all conditions and binding verbs.
    input: sections (dict) — dictionary of clause numbers to clause text from retrieve_policy.
    output: A string containing the full policy summary with all 10 required clauses, each referenced by number.
    error_handling: If a clause is missing from sections, flag it as [MISSING CLAUSE] in the output. If a clause contains multi-condition obligations, verify all conditions are preserved before including it.
