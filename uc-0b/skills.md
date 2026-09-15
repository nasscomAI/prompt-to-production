# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content as structured numbered sections.
    input: File path string (e.g. "../data/policy-documents/policy_hr_leave.txt")
    output: Dictionary mapping clause numbers (e.g. "2.3", "5.2") to their full text content
    error_handling: Raise an error if the file does not exist, is empty, or contains no parseable numbered sections

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary that preserves all clause obligations and conditions.
    input: Dictionary of clause number to full text (output of retrieve_policy)
    output: Summary text string with clause references, where each clause is either faithfully summarized or quoted verbatim with a flag
    error_handling: If any clause cannot be summarised without meaning loss, include it verbatim and flag it; refuse to output if fewer than 10 clauses are present
