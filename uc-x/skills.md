# skills.md — UC-X Ask My Documents Skills

skills:
  - name: retrieve_documents
    description: Loads all policy text files (HR, IT, Finance) and indexes their text content by document name and section numbers.
    input: Directory path or list of file paths to policy documents.
    output: Indexed document store supporting section-level retrieval by topic and keyword query.
    error_handling: Handles missing policy files by flagging unindexed documents and raising a document load warning.

  - name: answer_question
    description: Processes user questions against the indexed document store, retrieving matching sections and returning a single-source cited answer or the exact refusal template.
    input: User prompt question string.
    output: String response containing single-document answer with section citations, or the exact standardized refusal template.
    error_handling: Detects cross-document blending risks, out-of-scope topics, or ambiguous matches, returning the strict refusal template verbatim.
