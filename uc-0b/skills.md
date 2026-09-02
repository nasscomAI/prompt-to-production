skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns its content as structured numbered sections.
    input: Path to the policy .txt file.
    output: Structured policy sections with clause numbers and source text.
    error_handling: Reports missing or unreadable files instead of silently producing incomplete content.

  - name: summarize_policy
    description: Produces a compliant policy summary from structured sections while preserving every required clause and all of its conditions.
    input: Structured numbered policy sections.
    output: Summary containing clause references, obligations, conditions, deadlines, limits, approvers, and consequences.
    error_handling: Flags clauses that cannot be summarized without meaning loss and never silently removes conditions or adds unsupported information.