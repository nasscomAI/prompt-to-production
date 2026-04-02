# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause boundaries.
    input: File path to policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)
    output: Dictionary with keys for each numbered clause (e.g., 2.3, 2.4, etc.), values are clause text with binding verbs
    error_handling: If file not found, raise FileNotFoundError. If document lacks numbered structure, log warning and return raw text with section markers.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses with explicit binding verb and condition verification.
    input: Dictionary of policy clauses (output from retrieve_policy skill)
    output: Markdown summary with clause references, binding verbs, and all multi-condition obligations fully stated. Includes verification checklist of clauses.
    error_handling: If input is missing required clauses, flag them as [MISSING]. If a clause cannot be summarized without semantic loss, mark as [VERBATIM] and quote directly from source.
