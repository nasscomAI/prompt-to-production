skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: Directory path containing policy documents.
    output: Indexed document collection mapped by source and section.
    error_handling: Return error if directory is missing or files are unreadable.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer with citation OR refusal template.
    input: User query string, indexed document collection.
    output: Single-source answer with citation (Doc Name + Section) OR exact refusal template.
    error_handling: If information is missing, ambiguous, or requires cross-document blending, return exact refusal template.
