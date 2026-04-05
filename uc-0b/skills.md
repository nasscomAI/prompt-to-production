skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path string to the policy document.
    output: A structured format containing an array of clauses, each with a clause number and exact text.
    error_handling: Return an explicit error flag and descriptive message if the file is missing, empty, or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured array of clause sections from retrieve_policy.
    output: A precise summary with every point citing its original clause number and preserving all multi-condition obligations.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim, flag it, and return an explicit validation warning.
