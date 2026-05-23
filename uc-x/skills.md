# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None.
    output: A dictionary mapping document names and section numbers to their text content.
    error_handling: If any policy file is missing or unreadable, raise a FileNotFoundError.

  - name: answer_question
    description: Searches the indexed policy documents for the given query and returns either a single-source answer with citations or the exact refusal template.
    input: A query string and the indexed document structure.
    output: A string containing either the answer with citations or the exact refusal template.
    error_handling: If the query is ambiguous, requires cross-document blending, or cannot be answered, return the exact refusal template.
