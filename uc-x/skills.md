# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the 3 specified policy files and indexes them by document name and section number.
    input: File paths to the three .txt policy documents.
    output: A structured index or dictionary mapping document names and section numbers to their text content.
    error_handling: If a file is missing or unreadable, raise an error immediately. Do not attempt to guess or hallucinate missing text.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or the exact refusal template if the answer is not found.
    input: The indexed documents and a user's question string.
    output: A string containing either the factual answer with document/section citation, OR the exact verbatim refusal template.
    error_handling: If the answer requires blending information from multiple documents to form a conclusion, refuse the question using the exact refusal template to prevent cross-document hallucination.
