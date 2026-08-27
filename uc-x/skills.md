# skills.md
# UC-X — Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths to the policy documents.
    output: A structured index or database of the policy clauses.
    error_handling: Raise error if any of the three policy files are missing.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation or the exact refusal template.
    input: Question string and structured policy index.
    output: Formatted string containing the answer with citation, or the exact refusal text.
    error_handling: Always returns the refusal template if the answer requires cross-document blending, or if the answer cannot be confidently sourced.
