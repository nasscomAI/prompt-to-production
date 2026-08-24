skills:
  - name: retrieve_documents
    description: Loads all policy text files, parses them into structured sections, and indexes them by document name and section number.
    input: None
    output: A list of dicts containing indexed policy sections.
    error_handling: Handles missing policy files gracefully and reports indexing errors.

  - name: answer_question
    description: Processes a user query, searches the indexed documents, and returns a single-source answer with citations or the refusal template.
    input: question (str)
    output: The response string.
    error_handling: Returns the standard refusal template when the query matches no sections or causes cross-document ambiguity.
