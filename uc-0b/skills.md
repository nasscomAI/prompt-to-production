# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered clauses.
    input: file path string (e.g. "../data/policy-documents/policy_hr_leave.txt").
    output: JSON object {clauses: [{number: string, text: string}], raw_text: string}.
    error_handling: if file is missing, unreadable, or not in expected clause format, return a
      structured error with a clear message and do not proceed to summary.

  - name: summarize_policy
    description: Generates a compliant, obligation-preserving summary from structured policy clauses.
    input: JSON object from `retrieve_policy` (clauses array).
    output: text summary with explicit clause labels and each clause conclusion present.
    error_handling: if any clause is missing, clause conditions are not all represented, or policy
      text is malformed, return failure reason and include verbatim clause for fallback.

