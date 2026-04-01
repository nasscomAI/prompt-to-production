# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: "File path to a .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)."
    output: >
      A structured representation of the policy with each section (e.g., 1. PURPOSE AND SCOPE,
      2. ANNUAL LEAVE) and its numbered clauses (e.g., 2.1, 2.2, 2.3) preserved intact.
      Returns the full text of each clause including all conditions and binding verbs.
    error_handling: >
      If the file path is invalid, the file is empty, or the file does not contain
      recognisable policy structure (numbered sections/clauses), return an error message
      stating the specific issue. Do not attempt to guess or fabricate content.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references preserved.
    input: "Structured numbered sections as returned by retrieve_policy."
    output: >
      A clause-by-clause summary where each clause is referenced by its original number
      (e.g., 2.3, 5.2). All binding verbs (must, will, requires, not permitted) and
      all conditions within multi-condition obligations are preserved. No external
      information is added. Clauses that cannot be summarised without meaning loss
      are quoted verbatim and flagged with [VERBATIM — meaning-loss risk].
    error_handling: >
      If the input is missing sections, malformed, or empty, return an error identifying
      the problem. If a clause contains ambiguous language, preserve it exactly as-is
      rather than interpreting it. Never drop a clause silently — if a clause cannot
      be processed, flag it explicitly.
