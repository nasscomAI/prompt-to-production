skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (String).
    output: Content as structured numbered sections (JSON/Dictionary).
    error_handling: Raises an error if the file cannot be read or lacks recognizable numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections of the policy (JSON/Dictionary).
    output: Compliant textual summary with explicit clause references (String).
    error_handling: Refuses to summarize and returns exact verbatim text if a meaning cannot be preserved without loss.
