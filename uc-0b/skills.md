# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses its contents into structured numbered sections and clauses.
    input: File path string pointing to a policy text file (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: Structured dictionary or list of section objects, each containing section title and a map of clause numbers to clause text.
    error_handling: Raises FileNotFoundError with a clear message if the file is missing; raises ValueError if file is empty or contains no valid section headers.

  - name: summarize_policy
    description: Takes structured policy sections and generates an obligation-preserving summary with explicit clause references and all conditions intact.
    input: Structured sections from retrieve_policy, including all numbered clauses and obligation metadata.
    output: Plain-text formatted summary containing every numbered clause, preserved multi-conditions, and verbatim quotes where compression risks meaning loss.
    error_handling: Validates that all required binding clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are present; if any condition cannot be safely summarized without meaning loss, quotes the clause verbatim and marks it with [VERBATIM].
