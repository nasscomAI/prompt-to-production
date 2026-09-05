# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes their content by document name and section number.
    input: The file paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: An index mapping (document name, section number) to the section text, for all three documents.
    error_handling: If a file is missing or unreadable, raises a clear error listing which document could not be loaded. Any section that cannot be parsed is kept under its document with a marker rather than silently dropped.

  - name: answer_question
    description: Answers a single question from exactly one source document with a citation, or returns the refusal template.
    input: A user question (free text) and the document index built by retrieve_documents.
    output: A single-source answer with the document name and section number cited, or the exact refusal template when the question is not covered.
    error_handling: If the question maps to sections in more than one document, returns the refusal template instead of blending. If no section matches, returns the refusal template exactly with no hedging or invented content.