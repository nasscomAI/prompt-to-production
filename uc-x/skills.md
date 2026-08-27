# skills.md

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number.
    input: None required, or an optional search query string.
    output: Indexed collection of document sections.
    error_handling: Return an error if documents cannot be loaded.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User's question as a string.
    output: A factual single-source answer with citation, or the exact refusal template.
    error_handling: Return the exact refusal template if the answer is ambiguous, not covered, or requires blending multiple documents.
