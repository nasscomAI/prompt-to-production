# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: String path to the policy file.
    output: Dictionary mapping clause numbers to their full text.
    error_handling: Return appropriate error if file missing or cannot be parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Dictionary of structured numbered sections.
    output: String containing the complete summary.
    error_handling: If a clause cannot be safely summarized without meaning loss, quote it verbatim and flag it.
