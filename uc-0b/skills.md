skills:
  - name: retrieve_policy
    description: Reads the policy document and extracts its content.
    input: File path to policy text file.
    output: List of lines representing clauses from the document.
    error_handling: If file is missing or unreadable, return empty list.

  - name: summarize_policy
    description: Generates a clause-preserving summary from extracted policy text.
    input: List of clauses.
    output: Structured summary text with all clauses preserved.
    error_handling: If summarization risks losing meaning, return original clause instead.