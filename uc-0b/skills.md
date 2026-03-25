skills:
  - name: retrieve_policy
    description: Loads the policy text file and prepares it for section-by-section analysis.
    input: File path to the .txt policy document.
    output: Full text of the policy document.
    error_handling: Throws an error if the file is missing or unreadable.

  - name: summarize_policy
    description: Produces a high-fidelity summary by iterating through the 10 critical clauses and ensuring each is fully represented.
    input: Raw text content from retrieve_policy.
    output: A summary document formatted as a list of clauses with their core obligations and binding verbs.
    error_handling: If a critical clause (e.g., 5.2) cannot be found, it flags the output with "MISSING CRITICAL CLAUSE".
