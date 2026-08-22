# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy file and returns content as structured numbered sections.
    input: Path to .txt policy file (string).
    output: Structured list of clauses with clause number, obligation text, and binding verb.
    error_handling: If file is missing, unreadable, or unstructured, return "INVALID_INPUT" and skip summarisation.

  - name: summarize_policy
    description: Summarises structured policy sections into a compliant summary with clause references.
    input: Structured list of clauses from retrieve_policy.
    output: Text summary preserving all clauses, obligations, and conditions, with clause numbers referenced.
    error_handling: If summarisation risks meaning loss, quote the clause verbatim and flag it in the output.
