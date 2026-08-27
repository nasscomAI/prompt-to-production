# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to the .txt policy file (String).
    output: A collection of policy clauses mapped to their respective section numbers (JSON object).
    error_handling: Returns an error if the file path is invalid, inaccessible, or the file is not in .txt format.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with explicit clause references while preventing condition drops.
    input: Structured policy sections with clause numbers and text (JSON object).
    output: A high-fidelity summary string where each point is tagged with its source clause number.
    error_handling: Refuses to generate summary if key binding verbs are missing or if a clause cannot be summarized without losing multi-part conditions.
