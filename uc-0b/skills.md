skills:

* name: retrieve_policy
  description: Load the HR leave policy text file and return its contents as structured numbered sections and clauses.
  input: Path to the policy .txt file as a string.
  output: Structured collection of numbered policy sections and clauses preserving the original clause numbers and text.
  error_handling: Refuse processing if the file is missing, unreadable, empty, or cannot be parsed into numbered sections.

* name: summarize_policy
  description: Produce a clause-referenced summary of the structured policy while preserving every obligation, condition, deadline, limit, approver, and consequence.
  input: Structured policy sections and clauses from retrieve_policy.
  output: A text summary containing every required numbered clause with its original clause reference and preserved meaning.
  error_handling: If a clause is ambiguous or cannot be summarized without meaning loss, quote that clause verbatim and flag it rather than guessing or omitting conditions.
