# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured, numbered sections.
    input: File path to the .txt policy (string).
    output: List of structured clause objects (e.g., JSON or list of dicts with clause_id and content).
    error_handling: Return error if file not found, unreadable, or lacks identifiable numbering.

  - name: summarize_policy
    description: Processes structured policy sections to create a high-fidelity summary that preserves all binding obligations and conditions.
    input: List of structured clause objects.
    output: Formatted summary string with explicit clause references and preserved conditions.
    error_handling: Quote verbatim and flag any clause that cannot be safely summarized without meaning loss.
