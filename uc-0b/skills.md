skills:
  - name: retrieve_policy
    description: Loads HR policy text file and extracts numbered clauses as structured sections.
    input: Path to policy text file (.txt).
    output: List or dictionary of clause numbers with their corresponding policy text.
    error_handling: If file not found or text unreadable, return empty structure and log warning.

  - name: summarize_policy
    description: Generates clause-faithful summary ensuring all required obligations and approval conditions are preserved.
    input: Structured policy clauses.
    output: Text summary including clause references and strict obligations.
    error_handling: If a clause cannot be summarized without meaning loss, include verbatim clause and flag for review.