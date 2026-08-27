# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy documents and creates a searchable index by document name and section number.
    input: Document directory path (string) containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    output: Dict with keys: {document_name: {section_number: section_text, ...}, ...}. Each section extracted with metadata (document reference, version, effective date).
    error_handling: If any document is missing, raises FileNotFoundError with document name. If file encoding fails, retries with utf-8-sig. If section parsing fails, logs warning and continues with partial index.

  - name: answer_question
    description: Searches indexed documents for answer to question, returns exact citation with source document and section number, or uses refusal template if not found.
    input: question (string), document_index (dict from retrieve_documents), refusal_template (string)
    output: Dict with keys {answer: string, source_document: string, section_number: string, confidence: string} OR {refusal: string, reason: string} if not found or requires cross-document blending.
    error_handling: If question is ambiguous or requires information from multiple documents, returns refusal with explanation of which documents are involved. If question could be answered from multiple sections of same document, returns most specific section only.

