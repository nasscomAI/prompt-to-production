skills:
  - name: retrieve_documents
    description: Reads and indexes policy documents (HR, IT, Finance) into structured document sections with titles and clause numbers.
    input: Directory path or list of policy file paths.
    output: Indexed collection of sections mapped by document name and section number.
    error_handling: Handles missing policy files and logs unindexed sections.

  - name: answer_question
    description: Processes a user query against indexed policy documents to produce a single-source cited answer or the exact refusal template.
    input: Query string and indexed policy documents.
    output: String response containing factual answer with file + section citation, or exact refusal template.
    error_handling: Prevents cross-document blending and eliminates hedging phrases when question matches no single document.
