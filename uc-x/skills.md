skills:
  - name: retrieve_documents
    description: Loads the three policy text files, parses them, and indexes the content by document name and section number.
    input: None.
    output: A dictionary mapping document names and section numbers to the text content.
    error_handling: Reports an error if any of the three files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citations, or outputs the verbatim refusal template.
    input: User question (string) and indexed policy document dictionary.
    output: Answer string with document name and section citation, or refusal template.
    error_handling: Safeguards against cross-document blending and blocks any speculative answers.
