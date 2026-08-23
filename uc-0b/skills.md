skills:
  - name: retrieve_policy
    description: Load a policy text file and parse its numbered sections and clauses.
    input: Path to a UTF-8 .txt policy document.
    output: Sections with titles and ordered clause reference/text pairs.
    error_handling: Reject missing, unreadable, or unstructured input rather than guessing.

  - name: summarize_policy
    description: Render a traceable summary that preserves every source clause and condition.
    input: Structured sections returned by retrieve_policy.
    output: UTF-8 text with each numbered clause retained under its section.
    error_handling: Reject empty sections or any clause-count mismatch before writing output.
