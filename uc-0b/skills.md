skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content parsed into structured numbered sections for accurate tracking.
    input: File path to the policy text document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured representation (e.g., dictionary or list of objects) mapping section numbers to their full text content.
    error_handling: Raise an error if the file cannot be found or read. If a section lacks proper numbering, assign it to a default 'Unnumbered' section and log a warning.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that explicitly references clause numbers, preserves all conditions, and maintains original binding verbs.
    input: Structured numbered sections from the retrieve_policy skill.
    output: A compliant text summary document with exact clause references.
    error_handling: If a clause cannot be safely summarized without losing meaning or dropping conditions, output the clause verbatim and flag it. Fail the process if any of the mandatory 10 core clauses are missing from the input.
