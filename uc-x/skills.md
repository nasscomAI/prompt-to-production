skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes each numbered section by document name and section identifier.
    input: A folder path containing the policy documents, or a default repository path.
    output: A dictionary keyed by document name and section number, each holding the original text and normalized tokens.
    error_handling: If a policy file is missing or unreadable, raise a clear error and stop rather than guessing.

  - name: answer_question
    description: Finds the strongest single-source match for a question, returns the exact answer with citation, or returns the refusal template when the question is out of scope or requires cross-document blending.
    input: A natural-language question string and the indexed policy documents.
    output: A plain-text answer string that includes the source document and section number or the exact refusal sentence.
    error_handling: If multiple documents have similarly strong matches, refuse instead of blending them; if no match is found, return the refusal template exactly.
