# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A structured representation of the policy with each numbered clause extracted as a
      separate section, preserving clause numbers, headings, and full text including all
      binding verbs and conditions.
    error_handling: >
      If the file does not exist, is not a .txt file, or is empty/unreadable, return an
      error message stating the reason and refuse to proceed. Do not attempt to guess or
      reconstruct missing content.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: >
      Structured numbered sections produced by retrieve_policy — each section includes
      clause number, heading, and full text.
    output: >
      A clause-by-clause summary where each entry references its source clause number,
      retains all binding verbs (must, will, requires, not permitted) at original strength,
      preserves all multi-condition obligations in full, and contains no information absent
      from the source document. Clauses that cannot be summarised without meaning loss are
      quoted verbatim and flagged with [VERBATIM — meaning loss risk].
    error_handling: >
      If the input is not a structured policy document or contains no numbered clauses,
      refuse to summarise and state the reason. If a clause has ambiguous or contradictory
      conditions, flag it for human review rather than interpreting it.
