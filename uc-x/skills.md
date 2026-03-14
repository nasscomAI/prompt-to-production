skills:
  - name: retrieve_documents
    description: Loads and indexes all policy documents by document name and section number.
    input: Paths to HR, IT, and Finance policy text files.
    output: Structured dictionary mapping document names to section-wise content.
    error_handling: If any file is missing or unreadable, return error and stop answering.

  - name: answer_question
    description: Searches indexed policy content and returns a single-source answer with citation.
    input: User question string and structured policy index.
    output: Answer text citing document name and section number, or refusal template if not found.
    error_handling: If multiple documents seem relevant or answer unclear, refuse using the exact refusal template.