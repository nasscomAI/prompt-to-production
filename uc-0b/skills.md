# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

  - name: retrieve_policy
    description: >
      Reads the HR leave policy text file and extracts structured
      numbered clauses from the document.
    input: >
      Path to a .txt policy file.
    output: >
      List of clause objects containing clause number and text.
    error_handling: >
      If no clauses are detected return an empty list and flag
      NEEDS_REVIEW.

  - name: summarize_policy
    description: >
      Generates a compliance-safe summary where each clause
      is preserved and obligations are maintained.
    input: >
      Structured list of clauses.
    output: >
      Text summary preserving clause numbers and conditions.
    error_handling: >
      If summarization risks losing meaning quote the clause
      verbatim and flag VERBATIM_REQUIRED.