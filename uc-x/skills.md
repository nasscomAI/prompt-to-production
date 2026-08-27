skills:
  - name: retrieve_documents
    description: Loads all 3 CMC policy TXT files and indexes their content by document name and section number.
    input: List of file paths.
    output: Internal index dictionary: { 'doc_name': { '1.1': 'content', ... } }.
    error_handling: Return warning if any of the three files are missing before starting.

  - name: answer_question
    description: Answers a query using a single cited source from the indexed documents or returns the standard refusal template.
    input: query (str), context_index.
    output: String (cited answer OR refusal template).
    error_handling: Refuse to Answer any queries involving external knowledge or 'industry standards' not in the index.
