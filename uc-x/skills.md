skills:
  - name: retrieve_documents
    description: Ingests the 3 policy text files (HR, IT, Finance) and builds an indexed catalog of sections and clauses mapped by document name and clause identifier.
    input: docs_directory (str path to policy-documents folder or list of filepaths)
    output: dict mapping document names to structured sections and searchable clauses
    error_handling: Raises FileNotFoundError if any policy file is missing.

  - name: answer_question
    description: Matches user questions against indexed document clauses using single-source retrieval, returning exact citations and verified facts or triggering the standardized refusal template.
    input: question (str), indexed_docs (dict)
    output: answer (str containing citation or exact refusal template)
    error_handling: Strictly prevents cross-document synthesis; immediately triggers standard refusal template if query semantics do not match any policy clause.
