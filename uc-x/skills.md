# skills.md — UC-X Policy Question Answering Engine (Ask My Documents)

skills:
  - name: retrieve_documents
    description: Loads all three policy files (HR, IT, Finance) and parses them into a structured index organized by document name, section number, section title, and individual clauses with metadata.
    input: `file_paths` (list of str, file paths to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`).
    output: dict mapping document identifiers to structured document metadata (`doc_ref`, `version`, `effective_date`) and indexed sections containing `{section_number, section_title, clauses: [{clause_id, text, binding_terms}]}`.
    error_handling: Raises `FileNotFoundError` if any of the three policy files are missing; raises `ValueError` if a document is unreadable, empty, or fails section header validation.

  - name: answer_question
    description: Searches the indexed policy documents for clauses addressing the user query, verifies single-source provenance, and formats an evidence-backed answer with exact citations or triggers the refusal template.
    input: `query` (str, user's policy question) and `indexed_docs` (dict, structured document index from `retrieve_documents`).
    output: dict containing `{status: "ANSWERED" | "REFUSED", answer: str, source_doc: str, section: str, citation: str}` where `answer` preserves 100% of conditions, contains no cross-document blending or hedging, and provides exact document and section citations (or returns the verbatim refusal template when out-of-scope).
    error_handling: If the query topic is not present in the indexed documents, lacks clear policy backing, or cannot be resolved without cross-document blending/hedging, returns `status: "REFUSED"` with the exact refusal template citing the relevant department contact.
