skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: List of file paths to policy documents
    output: Indexed documents by document name and section number
    error_handling: Return error if files are missing or unreadable

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: User question as a string, and the indexed documents
    output: Single-source answer with citation, or the exact refusal template
    error_handling: If ambiguous or requires multi-document blending, return the refusal template exactly
