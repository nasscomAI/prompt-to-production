# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy text file and return structured numbered clause data.
    input: |
      - Type: string (file path)
      - Format: path to the policy text file, e.g. '../data/policy-documents/policy_hr_leave.txt'
    output: |
      - Type: dictionary/list
      - Format: [{"clause": "2.3", "text": "..."}, ...] for each clause found
    error_handling: |
      - If file not found: raise FileNotFoundError.
      - If file cannot be parsed into clauses: return empty list and set a parsing warning flag.
      - If input is not a string path: raise TypeError.

  - name: summarize_policy
    description: Generate a concise policy summary that includes all required clauses and preserves all conditions.
    input: |
      - Type: list of clause objects
      - Format: output from retrieve_policy, e.g. [{"clause":"2.3","text":"..."}, ...]
    output: |
      - Type: string
      - Format: text summary with every clause referenced and core obligation retained; optionally a separate set of flags for clause-specific issues.
    error_handling: |
      - If any of the ten required clauses is missing: include a missing clause warning and mark summary with NEEDS_REVIEW.
      - If a clause has been transformed in a way that drops conditions: quote original clause verbatim and mark the summary with a preservation warning.
      - If input is invalid type/form: raise TypeError.
      - If clause text is ambiguous or cannot be safely summarized: output the clause verbatim with a 'verbatim quote' annotation and flag for human review.
