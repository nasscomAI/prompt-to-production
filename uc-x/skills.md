skills:
  - name: retrieve_documents
    description: Loads and indexes the three mandatory policy files (HR, IT, and Finance) by document name and section number to facilitate precise, single-source retrieval.
    input: None (automatically accesses the three defined policy text files).
    output: A structured collection of policy clauses, each mapped to its source document name and specific section number.
    error_handling: Refuse to proceed and report a system error if any of the three mandatory policy files are missing, empty, or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents for a single-source answer to a user query, ensuring no cross-document blending.
    input: User query string.
    output: A factual response string derived from a single source document, including the document name and section number citation, OR the verbatim refusal template.
    error_handling: If the answer requires blending information from multiple documents, contains hedging phrases, or is not explicitly found in any document, return the verbatim refusal template.
