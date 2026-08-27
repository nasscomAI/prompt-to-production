skills:
  - name: retrieve_documents
    description: Loads all required policy files and indexes them systematically by document name and section number.
    input: List of file paths to policy documents (.txt format).
    output: A structured, searchable index mapping document names and section numbers to the extracted text content.
    error_handling: Return an initialization error if a document cannot be accessed or properly segmented.

  - name: answer_question
    description: Searches the indexed policy documents to provide a precise, single-source answer with citations.
    input: The user's query string and the generated document index.
    output: A factual answer citing the source document and section number, or the standard refusal template.
    error_handling: Return the exact refusal template if the answer is absent from the indexed documents or if it requires blending multiple distinct documents to address securely.
