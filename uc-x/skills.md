skills:
  - name: retrieve_documents
    description: Loads all 3 policy documents and indexes them by document name and section number.
    input: List of paths to policy documents.
    output: Indexed structure of policy document sections.
    error_handling: Handles missing files or unreadable files by reporting appropriate errors.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citations or the refusal template.
    input: User query string and indexed document structure.
    output: Answer string with document name and section citation, or the exact refusal template.
    error_handling: If the query is not found in the documents or if the answer would require blending sources, returns the exact refusal template.
