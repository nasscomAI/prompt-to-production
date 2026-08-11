# skills.md

skills:
  - name: retrieve_documents
    description: Loads the available policy documents and indexes their sections.
    input: None.
    output: Dictionary mapping document names to section numbers and text.
    error_handling: Raises an error if any required policy file is missing or unreadable.

  - name: answer_question
    description: Searches indexed policy documents and returns a single-source answer or the exact refusal template.
    input: Question text and indexed documents.
    output: Answer text with citation, or the refusal template.
    error_handling: Returns the refusal template if the question cannot be answered from a single document without blending.
