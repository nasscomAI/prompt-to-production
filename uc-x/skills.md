# skills.md

skills:
  - name: retrieve_documents
    description: Loads policy files (HR, IT, Finance) and indexes them by document name and section number.
    input: None. Reads from defined file paths in ../data/policy-documents/.
    output: A structured index or data structure of all policy content organized by source and section.
    error_handling: Logs descriptive error if any of the three mandatory files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents for a single-source answer and returns it with a citation or the mandatory refusal template.
    input: User's question as a string.
    output: A single-source answer string with a citation (document name and section) or the verbatim refusal template.
    error_handling: Returns the refusal template if the answer is not found, remains ambiguous, or would require blending across documents.

