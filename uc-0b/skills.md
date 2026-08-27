skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: A file path to a .txt policy document.
    output: Structured data with numbered sections from policy document, preserving the original content.
    error_handling: Returns an error message if the file is missing, unreadable, not in the expected format, or contains unsupported encoding. Attempts fallback encodings.

  - name: summarize_policy
    description: Produces a compliant summary of policy documents with clause references.
    input: Structured data with numbered sections from a policy document.
    output: A tabular summary with columns: Clause, Core obligation, and Binding verb. Each clause is explicitly structured to ensure clarity and compliance.
    error_handling: Flags and halts processing if any clause is missing, ambiguous, or violates enforcement rules. Ensures multi-condition obligations (e.g., double approvals) are preserved without omission.
