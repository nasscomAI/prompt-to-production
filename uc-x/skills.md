# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy documents and index their content by document name and section number without combining information across documents.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed policy content organized by source document and section number.
    error_handling: If a document is missing or unreadable, report the specific document error and do not invent replacement information.

  - name: answer_question
    description: Answer an employee policy question using a single supporting document and section citation, or return the exact refusal template when the question is unsupported or genuinely ambiguous.
    input: Employee policy question and indexed policy documents.
    output: A concise single-source answer with document filename and section number citations, or the exact required refusal template.
    error_handling: Refuse questions that are not covered, require unsupported cross-document blending, or cannot be answered without inference; never hallucinate or use hedged language.