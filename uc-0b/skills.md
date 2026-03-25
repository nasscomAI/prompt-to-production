# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: File path to the source .txt policy document (string).
    output: A collection of policy content structured by numbered sections (object/list).
    error_handling: Return an error if the file is missing, inaccessible, or does not follow a numbered format.

  - name: summarize_policy
    description: Transforms structured policy sections into a high-fidelity summary that preserves all core obligations and binding verbs.
    input: Structured policy sections with section numbers (object/list).
    output: A compliant summary where all 10 core clauses are represented and multi-condition obligations are preserved (string).
    error_handling: Refuse to generate a summary if the input sections are incomplete or if clauses Cannot be accurately mapped to the ground truth inventory.
