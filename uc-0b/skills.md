# skills.md — UC-0B Skills Specification

skills:
  - name: retrieve_policy
    description: Loads a plaintext policy file and parses its contents into structured sections and numbered clauses.
    input: Filepath to policy document (string, e.g. path to policy_hr_leave.txt).
    output: Structured dictionary or list mapping clause numbers (e.g., '2.3', '5.2') to their section title, exact clause text, and binding verbs.
    error_handling: Raises FileNotFoundError if file does not exist; returns an error description if the document contains no identifiable numbered clauses.

  - name: summarize_policy
    description: Takes structured numbered sections and generates a concise, high-fidelity summary ensuring all conditions, binding verbs, and approvers are preserved.
    input: Structured sections dictionary/list from retrieve_policy.
    output: Formatted string containing policy metadata, numbered clause summaries with preserved obligations, and flags for verbatim-quoted sensitive clauses.
    error_handling: Flags any clause containing multiple conditions with a validation check to guarantee no condition was dropped; warns if any numbered clause is missing.
