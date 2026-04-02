skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and segments it into structured sections and numbered clauses for analytical precision.
    input: String path to the policy .txt file.
    output: Structured object/list containing all policy sections with their associated numerical references.
    error_handling: Raises FileNotFoundError if the path is invalid or if the document structure is severely malformed.

  - name: summarize_policy
    description: Generates a high-fidelity summary from structured sections while enforcing the presence of critical ground-truth clauses.
    input: Structured sections from retrieve_policy and the classification rules from agents.md.
    output: A summary text string that preserves all binding conditions and approver roles.
    error_handling: Flags sections for manual review if a clause cannot be summarized without losing a quantifiable condition.
