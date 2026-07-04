skills:
  - name: retrieve_documents
    description: Loads policy documents and indexes their sections for search retrieval.
    input: List of file paths to the policy text files.
    output: Indexed database of sections.
    error_handling: Handles missing files gracefully without crashing.

  - name: answer_question
    description: Matches user question against the indexed documents, returning a single-source answer with citations or the refusal template.
    input: User query string and indexed database.
    output: Answer string with document and section citation, or the exact refusal template.
    error_handling: Returns the refusal template if the query is ambiguous or matches nothing.
