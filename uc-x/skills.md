skills:
  - name: retrieve_documents
    description: Loads all policy files and indexes them by document name and section number for precise searching.
    input: List of paths to policy text files.
    output: Indexed structure mapping sections to their content.
    error_handling: Fail if any file is missing or if section numbers cannot be uniquely identified.

  - name: answer_question
    description: Searches the indexed documents to provide a single-source answer with citations or the mandatory refusal template.
    input: User question (string) and indexed document metadata.
    output: A cited answer string or the exact refusal template if no match is found.
    error_handling: Refuse to answer if the query requires combining information from multiple documents.

