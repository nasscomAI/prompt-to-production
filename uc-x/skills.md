skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their sections by document name and section number.
    input: The directory path containing the policy documents.
    output: A nested dictionary indexing section numbers and content by document filename.
    error_handling: Handles missing files or incorrect directories, raising standard exceptions.

  - name: answer_question
    description: Searches the indexed policy documents for the query, matching keywords, verifying constraints, and returning single-source answers with citations or the refusal template.
    input: The user's query string and the indexed document structure.
    output: A string containing the answer with document and section citation, or the exact refusal template.
    error_handling: Automatically defaults to the exact refusal template if no matching section meets the relevance threshold or if a query spans multiple documents ambiguously.
