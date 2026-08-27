skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured, numbered sections to ensure accurate clause mapping.
    input: Path to the .txt policy file (String).
    output: Structured content grouped by numbered sections (Object/Dictionary).
    error_handling: Returns an error if the file is missing, unreadable, or doesn't follow the expected numbered format.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all core obligations and conditions with explicit clause references.
    input: Structured policy sections (Object/Dictionary).
    output: A high-fidelity summary text capturing references to the clauses from the inoput document.
    error_handling: Flags or refuses to summarize if a clause is ambiguous or if mandatory conditions (like multi-approver requirements) cannot be clearly stated without meaning loss.
