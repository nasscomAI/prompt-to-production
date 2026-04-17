# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Reads and parses a policy text file into structured, numbered sections.
    input: Path to a .txt policy file.
    output: A list of objects, each containing a 'clause_number' and 'content'.
    error_handling: Refuses to process if the file is not in .txt format or if no numbered clauses are detected.

  - name: summarize_policy
    description: Generates a compliance-focused summary of policy sections while preserving all obligations.
    input: A list of structured policy sections.
    output: A formatted text summary with explicit references to every clause.
    error_handling: If a clause contains multi-condition rules that cannot be simplified, it quotes them verbatim and adds a 'COMPLEXITY_FLAG'.
