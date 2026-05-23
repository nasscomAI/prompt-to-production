skills:
  - name: retrieve_documents
    description: Loads the three policy text files and parses/indexes their contents by document name and section number.
    input: None.
    output: A dictionary mapping document names and section numbers to their text content.
    error_handling: Raises a FileNotFoundError if any of the three policy documents are missing or inaccessible.

  - name: answer_question
    description: Searches the indexed policy content to retrieve a single-source answer with citations, or returns the verbatim refusal template.
    input: A dictionary containing the 'question' (string) and the 'indexed_documents' (dictionary structure from retrieve_documents).
    output: A string containing either the factual answer with exact citation (document name and section number) or the exact refusal template verbatim with no variations.
    error_handling: Strictly returns the verbatim refusal template if the question is ambiguous, not covered, or cannot be answered using a single source document.
