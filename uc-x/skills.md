# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads three policy text files and indexes them by document name and section number for retrieval.
    input: "Dict with paths to three policy files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output: "Dict with keys: documents (dict mapping doc_name → list of indexed sections), metadata (dict with doc_count, total_sections)"
    error_handling: "If file not found, log to stderr and skip document. If all files missing, raise error. If file unreadable, log encoding error and attempt recovery. Return available documents only."

  - name: answer_question
    description: Searches indexed documents for question answer, returns single-source citation with document and section OR refusal template.
    input: "String (user question) and indexed documents dict from retrieve_documents"
    output: "Dict with keys: answer (string), source_document (string), section_number (string), is_refusal (bool), blend_detected (bool)"
    error_handling: "If question matches multiple documents, set blend_detected=True and return refusal (refuse blend, don't answer). If question not found, return is_refusal=True with refusal template exactly. Never hedge or infer. If ambiguity detected, prefer refusal over guessing."
