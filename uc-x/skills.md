skills:
  - name: retrieve_documents
    description: Loads and indexes the policy documents by document name and section number.
    input: file paths of policy documents.
    output: structured dictionary of documents and their numbered sections.
    error_handling: if a document cannot be loaded, raise an error and stop execution.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation.
    input: user question and indexed document structure.
    output: answer text with source document name and section number or the refusal template.
    error_handling: if the question is not found in any document, return the refusal template instead of guessing.