skills:
  - name: retrieve_documents
    description: Load the three policy documents and index them by document name and section number.
    input: A base directory containing the policy documents.
    output: A dictionary keyed by document name and section number with the extracted policy text.
    error_handling: If a document is missing or unreadable, skip it and return an empty entry rather than guessing.

  - name: answer_question
    description: Search the indexed policy documents and return a single-source answer with a citation or the refusal template.
    input: A natural-language question string and the indexed policy documents.
    output: A plain-text answer string that either cites one applicable document section or repeats the refusal template exactly.
    error_handling: If the question is ambiguous or not covered, return the refusal template exactly.
