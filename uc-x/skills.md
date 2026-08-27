# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy documents, indexes them by document name and section number for fast retrieval and cross-reference detection.
    input: "Paths to three policy files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output: "Dictionary with keys: documents (dict mapping document_name → full text), indexed_sections (dict mapping 'document_name:section_number' → section_text). Example: {\"documents\": {\"policy_hr_leave.txt\": \"...\", ...}, \"indexed_sections\": {\"policy_hr_leave.txt:2.6\": \"...\"}}"
    error_handling: "If any file not found, raise error with file path. If file is empty or unreadable, raise error. Parse section numbers and warn if non-standard sections detected (should be X.Y format). Return indexed structure even if some sections are malformed, but log warnings."

  - name: answer_question
    description: Searches indexed documents for question-related content, returns single-source answer with citation OR the mandatory refusal template if question is not in documents.
    input: "Question (string), indexed_sections (dict from retrieve_documents), refusal_template (string)"
    output: "Answer string with explicit citation format '{ANSWER} [SOURCE: document_name.txt, Section X.Y]' OR the refusal template exactly. Example: 'Max 5 days can be carried forward, forfeited on 31 Dec. [SOURCE: policy_hr_leave.txt, Section 2.6]'"
    error_handling: "If question matches content in multiple documents, return only the single best source or refuse. If answer requires blending multiple sections from same document, cite both sections. Never use hedging language — either answer with citation or refuse. If unclear whether to answer or refuse, err toward refusal. Log which documents were searched and why answer was selected or refused."
