# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: file_path (str, path to a policy .txt file).
    output: The full text content of the policy document, preserving all section numbers, clause numbers, and exact wording.
    error_handling: If the file is not found or unreadable, prints an error message and exits. Never fabricates content for a missing file.

  - name: summarize_policy
    description: Takes structured policy text and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: The full text of a policy document (str).
    output: A structured summary where each numbered clause is represented with its section reference, core obligation preserved, binding verbs intact, and all conditions listed. Written to an output .txt file.
    error_handling: If a clause cannot be summarized without meaning loss, it is quoted verbatim and flagged. Never silently drops clauses or conditions.
