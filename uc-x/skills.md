skills:
  - name: retrieve_documents
    description: Ingests the 3 municipal policy text files, parses sections and numbered clauses, and builds an in-memory single-source document index with document names and section citations.
    input: Base directory path containing policy document txt files.
    output: Indexed dictionary mapping document names and section IDs to section headers, texts, and rules.
    error_handling: Raises FileNotFoundError if any of the three policy files are missing; logs warnings on malformed section headers.

  - name: answer_question
    description: Queries the indexed policy repository, identifies the single authoritative source section, formulates a precise citation-backed answer without hedging or blending, or returns the exact refusal template.
    input: Question string from user and the document index.
    output: String containing single-source factual answer with [document Section X.X] citation, or the exact refusal template.
    error_handling: Detects cross-document blending hazards and ungrounded queries, defaulting directly to the mandatory refusal response.
