skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and parses them into a structured index mapped by document name and section number.
    input: None (or list of file paths).
    output: Dictionary containing indexed policy sections.
    error_handling: Refuses to start if any of the three policy files are missing or unreadable.

  - name: answer_question
    description: Processes a user's question, performs precise keyword matching across the indexed policy documents, and returns a single-source answer with proper citation, or the exact refusal template.
    input: Question string (string).
    output: Answer string with document name and section citation (string).
    error_handling: Returns the exact refusal template if no matching source is found or if the question is ambiguous/blends multiple sources.
