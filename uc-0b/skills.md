# skills.md

skills:
  - name: retrieve_policy
    description: Loads a designated .txt policy file and returns its content as structured, numbered sections.
    input: File path to the policy text document (string).
    output: A structured object mapping clause numbers to their exact text content.
    error_handling: If the file is not found or unreadable, return an error indicating the file could not be parsed.

  - name: summarize_policy
    description: Takes the structured sections from the policy and produces a highly compliant summary of targeted clauses, ensuring all conditions from the source text are strictly preserved.
    input: The structured clauses object from retrieve_policy.
    output: A formatted string summarizing all the targeted clauses without losing conditional meanings.
    error_handling: If a clause cannot be confidently summarized without losing its legal meaning or conditions, quote it verbatim and flag it as a direct quote.
