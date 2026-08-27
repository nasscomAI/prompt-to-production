skills:
  - name: retrieve_documents
    description: Loads and indexes all policy documents by section.
    input: File paths of policy documents
    output: Dictionary with document name and section-wise content
    error_handling: Raises error if file not found or empty

  - name: answer_question
    description: Searches documents and returns single-source answer or refusal.
    input: User question + indexed documents
    output: Answer string with citation OR refusal template
    error_handling: If multiple sources match or no clear match → return refusal template