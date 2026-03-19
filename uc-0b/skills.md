skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections for precise analysis.
    input: Path to the .txt policy file.
    output: Structured representation of policy sections, preserving original numbering.
    error_handling: Returns an error if the file is not found or is in an invalid format.

  - name: summarize_policy
    description: Produces a high-fidelity summary of structured policy sections, ensuring no clauses are omitted and all conditions are preserved.
    input: Structured policy sections (from retrieve_policy).
    output: A compliant summary where every numbered clause is accounted for and multi-condition obligations are intact.
    error_handling: If a clause cannot be summarized without losing critical meaning, quotes the clause verbatim and flags it for review.
