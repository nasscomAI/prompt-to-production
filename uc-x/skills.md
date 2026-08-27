# skills.md

skills:
  - name: retrieve_documents
    description: Load the available policy files and index them by document name and section.
    input: A directory path containing the policy documents.
    output: A dictionary of document names mapped to their text contents.
    error_handling: If a required document is missing, continue with the available files and use the refusal template when necessary.

  - name: answer_question
    description: Search the indexed documents and return a single-source answer or the required refusal template.
    input: A user question string.
    output: A string answer containing either a document-backed policy response or the refusal template.
    error_handling: If no single-source answer is available, return the refusal template exactly.
