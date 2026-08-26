# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all policy text files in data/policy-documents/ and indexes content by document name and section number.
    input: Directory path containing policy text files (docs_path).
    output: Searchable index/dictionary mapping document names and section identifiers to section text.
    error_handling: Reports unreadable files or malformed section headings during index construction.

  - name: answer_question
    description: Searches indexed policy documents for relevant sections and returns a single-source answer with citations or the exact refusal template.
    input: User query string (question) and indexed policy document object.
    output: Answer string containing cited document name and section number, OR exact refusal template.
    error_handling: Returns exact refusal template if query requires cross-document speculation or lacks single-source coverage.
