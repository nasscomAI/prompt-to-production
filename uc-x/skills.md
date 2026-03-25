skills:
  - name: retrieve_documents
    description: Loads all three policy documents and builds a searchable index by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed document structure with section identifiers, section text, and source document metadata.
    error_handling: If any file is missing, unreadable, or lacks parsable sections, return an explicit load/index failure and block answering until resolved.

  - name: answer_question
    description: Finds the best single-document section match and returns a citation-backed answer or the exact refusal template.
    input: User question text plus indexed policy documents from retrieve_documents.
    output: Either a single-source answer with source document name and section number for each factual claim, or the exact refusal template.
    error_handling: Refuse when evidence is absent, conflicting, or requires cross-document blending; never use hedging language or inferred policy interpretation.
