# skills.md

skills:
  - name: retrieve_documents
    description: Load the three policy documents and index them by document name and section number.
    input: Paths to the HR leave, IT acceptable use, and finance reimbursement documents.
    output: A nested mapping of document names to section numbers and section text.
    error_handling: If a document is missing, raise a file-not-found error. If section parsing fails, retain the raw text and flag the issue.


  - name: answer_question
    description: Search indexed documents for the best single-source answer or refuse with the exact refusal template when the question is not covered.
    input: The indexed document set and a user question string.
    output: A single answer string plus citation metadata, or the refusal template if no valid answer exists.
    error_handling: If the question is not covered or if multiple documents provide conflicting answers, return the refusal template exactly instead of blending.
