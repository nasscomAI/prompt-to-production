# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three CMC policy documents from disk, parses them into indexed sections by document name and section number, and returns a searchable document store.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A dictionary keyed by document name (e.g. "HR-POL-001"), where each value is a dictionary of section_number -> section_text. Includes a flat index mapping section numbers across all documents.
    error_handling: If any of the three files is missing or unreadable, raise a clear error naming the missing file. If a document has unnumbered sections, include them under a key "unnumbered" and log a warning. Never proceed with fewer than all three documents loaded.

  - name: answer_question
    description: Takes a user question and the indexed document store, searches for the most relevant single source, and returns either a cited answer or the exact refusal template.
    input: A question string and the document store from retrieve_documents.
    output: A dictionary with keys: answer (string), source_document (name and section number, or "none"), citation (verbatim quote from source, or the refusal template text).
    error_handling: If the question is empty or unparseable, respond with the refusal template. If multiple documents seem equally relevant and cannot be disambiguated, respond with the refusal template rather than blending. If no section matches the question topic, respond with the refusal template.
