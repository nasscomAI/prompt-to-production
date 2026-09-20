# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as structured numbered sections.
    input: File path to a .txt policy document (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: Ordered list of {clause_number, text} preserving original wording, numbers, and AND/OR conditions; missing file raises an error.
    error_handling: FileNotFoundError with path if missing; empty file returns empty list and downstream step quotes nothing rather than inventing clauses; never fills gaps from external knowledge.

  - name: summarize_policy
    description: Condense structured clauses into a compliant summary with one numbered item per required clause.
    input: Structured clause list from retrieve_policy plus the required set {2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2}.
    output: Plain-text summary where every item starts with [clause-number], preserves all conditions, AND/OR, numbers, deadlines, binding verbs (must/will/requires/not permitted), and adds no external rules; unsafe clauses are quoted verbatim with [QUOTED VERBATIM].
    error_handling: If a required clause number is absent from source, emit "[X] Not found in source — [QUOTED VERBATIM] unavailable" instead of guessing; never drops a condition silently.
