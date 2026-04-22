# skills.md — UC-X Policy Retrieval Specialist

skills:
  - name: retrieve_documents
    description: Aggregates and indexes multiple policy documents by source name and section ID.
    input:
      type: array
      items: string (Paths to HR, IT, and Finance .txt policies)
    output:
      type: map
      keys: doc_name
      values: array of clause objects (id, content)
    error_handling: Verifies document integrity (Doc ID, Version) during indexing; skip corrupted files with a warning.

  - name: answer_question
    description: Processes user queries against the index to return single-source verified answers with citations.
    input:
      type: string (Natural language question)
    output:
      type: object
      fields:
        answer: string (Fact-based response with no hedging)
        source: string (Format: [Document Name] section [ID])
    error_handling: If no single source contains the complete answer, or if documents conflict, MUST return the standard refusal template.
