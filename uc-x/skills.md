skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy files by document name and section number for retrieval.
    input: "File paths (../data/policy-documents/policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)"
    output: "Dictionary: {document_name → {section_id → section_text}}"
    error_handling: "If file missing or unreadable, return error with file path. Do not proceed with partial index."

  - name: answer_question
    description: Searches indexed documents for single-source answer; returns answer + citation or refusal template.
    input: "User question (string); indexed document dictionary from retrieve_documents"
    output: "Object: {answer (string), source (document_name + section_number), or refusal_template (string)}"
    error_handling: "If answer found in multiple documents, return refusal template (ambiguous — requires cross-document blend). If not found in any document, return refusal template. Never return hedged or synthesized answers."
