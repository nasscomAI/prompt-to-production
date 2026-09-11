# skills.md — UC-X

skills:

  - name: retrieve_documents
    description: Load all three policy documents and index their content by document name and section number.
    input: Three policy .txt file paths containing numbered policy sections.
    output: A structured collection of policy sections indexed by document name and section number.
    error_handling: If a document is missing, unreadable, or invalid, report the error and do not invent or reconstruct missing content.

  - name: answer_question
    description: Search the indexed policy documents and return a single-source answer with a document and section citation, or the exact refusal template when the question is not covered.
    input: A user policy question and the indexed policy documents.
    output: An answer based on one source document with document name and section number, or the exact refusal template when the question is not covered.
    error_handling: Never blend claims from different documents. If the question is not covered or the answer would require combining documents or guessing, return the exact refusal template.