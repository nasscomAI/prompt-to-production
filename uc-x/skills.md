# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files, indexes by document name and section number for retrieval.
    input: "List of file paths: [policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt]"
    output: "Object: {success: bool, error: str or None, documents: {document_name: {sections: {section_id: section_text}, full_content: str}}, index: {document_name: [section_ids]}, ready: bool}"
    error_handling: "If any file does not exist, returns {success: false, error: 'FILE_NOT_FOUND: [file_path]'}. If file is empty or unreadable, returns {success: false, error: 'FILE_UNREADABLE: [reason]'}. Does NOT partially load — all three documents must load successfully for success: true"

  - name: answer_question
    description: Searches indexed documents for a question, returns single-source answer with citation OR refusal template if not covered.
    input: "Object: {question: string, documents: indexed_documents, refusal_template: string}"
    output: "Object: {success: bool, answer: string, source_document: string or null, section_id: string or null, is_refusal: bool, search_confidence: float (0-1)}"
    error_handling: "If question is ambiguous or would require cross-document blending, returns is_refusal: true with refusal_template. If question is not in documents, returns is_refusal: true. If documents are not indexed, returns {success: false, error: 'DOCUMENTS_NOT_INDEXED'}. Never returns partial answers or hedged responses. Either returns complete single-source answer with citation, or refusal — no middle ground."
