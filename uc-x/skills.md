skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number for retrieval.
    input: None (initialization only). Loads from ../data/policy-documents/policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Indexed document map (dict): {document_name: {section_id: section_text, ...}, ...}. Sections parsed and keyed by document + section number (e.g., "policy_hr_leave.2.6").
    error_handling: Fail explicitly if any policy file is missing or unreadable. Return error message with file path. Do not proceed with partial document set.

  - name: answer_question
    description: Searches indexed documents for the question's answer, returns single-source answer with citation or the refusal template.
    input: String (question), indexed_documents dict (from retrieve_documents). Example: "Can I carry forward unused annual leave?"
    output: Object with fields {answer: string, source: "document_name.section_id", type: "answer" | "refusal"}. If answer found: cite exact section. If not found: use refusal template exactly with no variation.
    error_handling: If question is ambiguous or spans multiple documents, return refusal (do not blend). If question is unanswerable from single source (e.g., cross-document trap), return refusal template. Never return hedging phrases or speculation.
