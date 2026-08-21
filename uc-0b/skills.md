# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content organized into structured, numbered sections.
    input: File path string to the raw `.txt` policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: A structured dictionary mapping section headers or numbers to their respective textual content.
    error_handling: Refuses operation and returns an explicit error stating "Failed to parse text format." if the document cannot be loaded or is corrupted.

  - name: summarize_policy
    description: Takes structured sections from a policy document and produces a fully compliant summary with explicit clause references, maintaining all core obligations.
    input: Structured policy content (output from `retrieve_policy`).
    output: A formatted string containing the compliant summary, with every numbered clause referenced and all conditions met.
    error_handling: Returns "INCOMPLETE SUMMARY EXCEPTION: Missing Clause [X]" if the resulting summary drops any clauses or detected conditions.
