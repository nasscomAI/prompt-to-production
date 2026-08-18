skills:
  - name: retrieve_documents
    description: Ingests and indexes policy text documents (HR, IT, Finance) by document name, section number, and individual clause text.
    input: doc_paths (list of str - filepaths to policy text documents)
    output: dict mapping document_name to structured sections and clause contents
    error_handling: Handles missing policy files safely and logs missing document paths.

  - name: answer_question
    description: Resolves an employee query against indexed policy documents, returning a single-source answer with document name and section citation, or the standard refusal template.
    input: query (str - user question), indexed_docs (dict - parsed document corpus)
    output: dict containing {answer: str, source_document: str, section: str, is_refusal: bool}
    error_handling: Refuses answers if confidence is low, if topic is not present, or if an answer would require unverified multi-document blending.

