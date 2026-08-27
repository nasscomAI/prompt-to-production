skills:
  - name: retrieve_policy
    description: Loads the policy text file and returns the policy content organized by numbered clause sections.
    input: text file path to a policy document (.txt)
    output: structured numbered sections with clause text for each clause
    error_handling: returns an error when the file is missing or unreadable; if clause sections cannot be parsed reliably, signals invalid input and does not invent clauses

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves every clause and its conditions.
    input: structured numbered sections from retrieve_policy
    output: compliant summary text including all numbered clauses and preserving all conditions
    error_handling: returns an error when input is invalid or incomplete; if a clause cannot be summarized without meaning loss, quotes it verbatim and flags it
