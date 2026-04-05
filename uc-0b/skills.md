skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and converts it into structured numbered sections.
    input:
      type: file_path
      format: plain text (.txt) policy document
    output:
      type: structured_sections
      format: list of numbered clauses with clause id and text
    error_handling: >
      If the file is missing, unreadable, or empty, return a clear error message.
      If numbered clauses cannot be identified reliably, preserve raw text and flag
      the structure as incomplete instead of guessing.

  - name: summarize_policy
    description: Produces a clause-preserving summary of the structured HR leave policy with clause references.
    input:
      type: structured_sections
      format: list of numbered clauses with clause id and text
    output:
      type: summary_text
      format: clause-by-clause compliant summary with clause references
    error_handling: >
      If a clause contains multiple conditions, preserve all of them explicitly.
      If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.
      If source wording is ambiguous, do not invent meaning; preserve the original wording as closely as possible.