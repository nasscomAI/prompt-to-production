skills:
  - name: retrieve_documents
    description: Loads the three organizational policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes their contents into structured records by document name and numbered section.
    input: List of file paths or directory path pointing to the three policy text files.
    output: Structured collection (list or dictionary) of indexed sections containing document_name, section_number, section_title, and section_text.
    error_handling: Raises FileNotFoundError or an explicit error if any of the required policy files are missing, unreadable, or empty; refuses to fabricate or interpolate missing policy content.

  - name: answer_question
    description: Queries the indexed policy documents to produce a verifiable, single-source response with exact document and section citations, or returns the exact refusal template.
    input: String question and the indexed policy document collection (from retrieve_documents).
    output: String response containing verified single-source facts citing source document name and section number, or the exact refusal template string.
    error_handling: Strictly refuses cross-document blending, hedged phrases, or condition dropping; returns the verbatim refusal template ('This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.') whenever a question is unaddressed, out-of-scope, or generates unresolvable cross-document ambiguity.
