skills:
  - name: retrieve_documents
    description: Loads the three policy files (HR, IT, Finance) and indexes them by document name and section number for precise retrieval.
    input: Paths to the three policy documents.
    output: An indexed knowledge base of policy sections.
    error_handling: Reports an error if any of the three required policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed knowledge base to provide a single-source answer with proper citations or the standard refusal template.
    input: User question (String) and indexed knowledge base.
    output: A single-document sourced answer with citations or the exact refusal template.
    error_handling: Strictly avoid blending documents; if an answer cannot be sourced from one document alone without ambiguity, return the refusal template.
