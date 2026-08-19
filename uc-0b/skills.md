# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Load the HR policy text and return its numbered clauses as structured sections.
    input: Plain-text policy file path.
    output: Structured list of numbered policy clauses with their original text.
    error_handling: Return an error if the file cannot be read or if numbered clauses cannot be identified.

  - name: summarize_policy
    description: Produce a clause-complete summary while preserving every obligation and condition.
    input: Structured numbered policy sections.
    output: Plain-text summary containing clause references and faithful summaries.
    error_handling: Preserve the original clause text and flag it for review if summarization could lose meaning.