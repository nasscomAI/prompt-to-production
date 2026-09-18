# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt (or a directory containing them).
    output: An index mapping {document_name: {section_number: exact clause text}} for all three documents.
    error_handling: Raises an error if any required document is missing or unreadable; failure to load one document aborts rather than answering from a partial set.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the fixed refusal template when the question is not covered.
    input: A question string and the document index from retrieve_documents.
    output: A plain-text answer resting on ONE document (with document name + section number cited), or the verbatim refusal template.
    error_handling: Refuses with the fixed template when nothing in the documents answers the question; refuses instead of ever blending claims from two documents into one answer.
