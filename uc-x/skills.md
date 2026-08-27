# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes them by document name and section number.
    input: File paths to the three policy documents (txt format).
    output: Indexed data structure containing document text mapped to metadata (name and section).
    error_handling: Return a clear error if any file is missing or unreadable; do not attempt to proceed with partial data.

  - name: answer_question
    description: Searches the indexed documents for a specific query and returns a single-source answer with citation or the refusal template.
    input: User question (string) and indexed document data.
    output: Answer string with document name and section citation, or the exact refusal template.
    error_handling: If the query is ambiguous across documents or not found, default immediately to the refusal template.
