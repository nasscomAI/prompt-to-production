skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured, numbered sections.
    input: A file path to the raw policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: The exact content of the policy organized into structured, verbatim numbered sections.
    error_handling: If the file is inaccessible or cannot be parsed, refuse rather than guess the contents.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant, condition-preserving summary with clause references.
    input: Structured numbered sections strictly originating from the retrieve_policy skill.
    output: A precise summary maintaining all multi-condition obligations and binding verbs, mapped correctly to source clauses.
    error_handling: If summarization attempts to silently drop condition requirements (like multiple approvers) or add external standard practices, refuse and instead quote the clause verbatim and flag it.
