skills:
  - name: retrieve_documents
    description: Loads the three policy documents and indexes them by document name and section number for fast lookup.
    input: Paths to the three policy files (strings) or a directory containing them.
    output: An in-memory index mapping each document and section number to its text content.
    error_handling: If any file is missing, unreadable, or cannot be parsed into sections, abort with a descriptive error.

  - name: answer_question
    description: Searches the indexed documents for a user question and returns a single-source answer with citation or the exact refusal template.
    input: A user question (string) and the document index from `retrieve_documents`.
    output: A string containing either a factual response with source citation or the refusal template.
    error_handling: If the answer requires blending multiple documents or the question is unsupported, return the exact refusal template with no variations.
