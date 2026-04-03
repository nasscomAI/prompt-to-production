skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and structurally indexes them by their document name and section number.
    input: List of file paths to the policy documents.
    output: A structured index mapping document names and section numbers to the exact text.
    error_handling: System safely handles missing documents by logging read-errors and skipping them securely.

  - name: answer_question
    description: Searches indexed documents specifically to formulate a single-source answer with detailed citations, or it flatly refuses the query.
    input: The user query string and the indexed structured document context.
    output: The single-source text answer with citations (Document Name, Section), or exactly the required refusal template.
    error_handling: Refuses ambiguous combinations and non-covered questions unconditionally by outputting the specific refusal template exactly.
