skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections
    input: Valid file path to the .txt policy document (String)
    output: Structured representation of the policy document with clearly numbered sections (JSON/Dict)
    error_handling: Return a clear error if the file cannot be accessed, read, or parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references
    input: Structured numbered sections of the policy document (JSON/Dict)
    output: A verifiable text summary of the policy retaining all core clauses, explicitly citing clause numbers and preserving multi-condition obligations (String)
    error_handling: Return an error or quote verbatim if a clause cannot be confidently summarized without losing multi-condition obligations or altering original meaning.
