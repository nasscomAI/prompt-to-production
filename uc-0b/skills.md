# skills.md — UC-0B Policy Parsing and Summarization

skills:
  - name: retrieve_policy
    description: Loads a plain text policy document and parses it into a structured format of numbered sections and clauses.
    input: Path to a .txt policy file.
    output: A structured object or list of strings containing the original text of each numbered clause.
    error_handling: Return an error if the file format is invalid or if numbered sections cannot be reliably identified.

  - name: summarize_policy
    description: Processes structured policy content to create a summary that preserves every core obligation and multi-part condition as per agents.md.
    input: Structured policy content (output from retrieve_policy).
    output: A summarized text file where every clause is represented, citing the original clause numbers.
    error_handling: If a clause is identified as 'high-risk' for meaning loss during summarization, the skill must return the clause text verbatim.
