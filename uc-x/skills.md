# skills.md — UC-X Ask My Documents

skills:

  - name: retrieve_documents
    description: Loads all three supplied policy documents and indexes their contents by document name, section number, and source text.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Structured document index containing document names, section numbers, and corresponding policy text.
    error_handling: If a document cannot be loaded or a section cannot be parsed reliably, report the problem rather than inventing missing policy content.

  - name: answer_question
    description: Searches the indexed policy documents and answers a question using information from exactly one source document.
    input: User question and the structured document index returned by retrieve_documents.
    output: A single-source answer with document name and section number citations, or the exact refusal template when the question is not covered.
    error_handling: If answering would require combining facts from multiple documents, or if no document provides sufficient support, return the exact refusal template instead of guessing or blending information.