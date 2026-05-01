skills:
  - name: retrieve_documents
    description: Loads all three policy files (HR, IT, Finance) and indexes their contents by document name and section number.
    input: None or specific file paths to the policy documents (strings).
    output: Indexed documents mapping document names and section numbers to text content (dictionary).
    error_handling: Raises an error and halts execution if any of the three required policy documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source factual answer or the exact refusal template.
    input: User question (string) and the indexed documents.
    output: Factual answer citing source document name and section number, or the refusal template (string).
    error_handling: If the answer requires blending claims from multiple documents, or if the question is not covered, it strictly returns the exact refusal template without any hedging phrases.
