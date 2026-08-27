skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: file path as string (e.g., policy_hr_leave.txt)
    output: A list or structured dictionary of numbered sections with their textual content.
    error_handling: If the file does not exist or cannot be read, raise a clear error specifying the missing file.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references.
    input: Structured policy sections (text/list of dicts).
    output: A numbered summary document as a string that strictly complies with policy summarization rules.
    error_handling: If an obscure clause is found, it is quoted verbatim and flagged. If input lacks numbered clauses, it raises an exception indicating the source format is invalid.
