# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: String file path to a .txt policy document.
    output: Dictionary mapping section numbers to their text content.
    error_handling: Raises FileNotFoundError with a clear message if the file is missing or unreadable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all binding obligations.
    input: Dictionary of structured numbered sections from retrieve_policy.
    output: Formatted string summary with every clause referenced, obligations preserved, and verbatim quotes where meaning loss would occur.
    error_handling: If a clause cannot be summarised without meaning loss, flags it with [VERBATIM] and quotes it exactly.
