# skills.md — UC-X Knowledge Retrieval

skills:
  - name: retrieve_documents
    description: Ingests multiple text-based policy documents and organizes them into a searchable index partitioned by section numbers.
    input: List of file paths to policy documents (.txt).
    output: A structured database or index mapping every section across all documents to its specific raw content.
    error_handling: Notifies the user if a document cannot be read or if sections cannot be clearly identified.

  - name: answer_question
    description: Retrieves the most relevant single-source section for a user query and formats an answer using strict citation and refusal rules.
    input: User natural language question.
    output: A cited answer [Document, Section] or the standardized refusal template if the answer is missing or uncertain.
    error_handling: If document blending is detected or if multiple conflicting sources are found, the system defaults to the refusal template to ensure safety.
