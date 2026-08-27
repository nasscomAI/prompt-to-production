# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a .txt policy file.
    output: List of dictionaries, each with 'clause', 'text', and optionally 'binding_verb'.
    error_handling: Raises an error if the file is missing or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: List of dictionaries as output by retrieve_policy.
    output: String containing the summary, with all clauses present and referenced.
    error_handling: If a clause cannot be summarized without meaning loss, quotes it verbatim and flags it in the output.
