skills:
  - name: retrieve_documents
    description: Load the three policy text files and index their numbered sections.
    input: Paths to the three policy documents.
    output: A dictionary mapping document names to section IDs and section text.
    error_handling: Raises an error if any document cannot be found or if document indexing fails.

  - name: answer_question
    description: Match a user question to the correct policy section and return a single-source answer with citation, or refuse if not covered.
    input: Indexed policy documents and a user question string.
    output: A string answer citing document name and section number, or the exact refusal template.
    error_handling: Refuses cleanly when the question is not covered, and avoids combining information from multiple documents.
