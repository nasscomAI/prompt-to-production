skills:
  - name: retrieve_documents
    description: Loads and parses the three corporate policy text files, indexing the text content by file name and section/clause number.
    input: None.
    output: A list of dictionaries representing the indexed policy sections.
    error_handling: Handles missing text files by printing warnings and proceeding with the remaining files.

  - name: answer_question
    description: Takes an input question, searches the indexed documents, and returns a single-source answer with proper citation or the refusal template.
    input: A query string and the list of indexed document sections.
    output: An answer string with citation or refusal.
    error_handling: Refuses to answer or falls back to the refusal template if the question matches multiple files causing ambiguity, or if no single source can answer the query.
