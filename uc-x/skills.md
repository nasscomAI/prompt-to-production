skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: No input required (uses hardcoded paths to the 3 policy documents).
    output: A structured index mapping document names and section numbers to their text content.
    error_handling: Raise an exception if any of the three policy files cannot be located or read.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with citation, OR the refusal template.
    input: The user's question (string) and the retrieved document index.
    output: A string containing either the answer (with source document and section citation) OR the exact refusal template.
    error_handling: Return the exact refusal template if the answer requires blending multiple documents, if the documents contradict, or if the question is absent.
