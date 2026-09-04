skills:
  - name: retrieve_documents
    description: Ingests the 3 municipal policy text files (HR, IT, Finance) and builds a structured, in-memory index partitioned by document filename and section/clause number.
    input: List of filepaths or directory path containing the policy documents.
    output: Indexed dictionary mapping document names to structured sections, clauses, and searchable keywords.
    error_handling: Handles missing policy files or malformed files by raising descriptive errors during index construction.

  - name: answer_question
    description: Processes a citizen or employee inquiry against indexed policy sections, generating a single-source response with exact document and section citations, or returning the standard refusal template for uncovered topics.
    input: question (str) representing the user query, and optional indexed policy knowledge base.
    output: Formatted string containing the verified single-source answer and explicit citation, or the standard refusal template.
    error_handling: Refuses out-of-scope or unanswerable queries cleanly without speculation, hedging, or cross-document blending.
