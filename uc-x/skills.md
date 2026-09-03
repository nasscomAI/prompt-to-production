# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads the three corporate policy text files, parses them into discrete
      numbered sections, and indexes them by document filename and section number.
    input: >
      doc_paths (dict or list of str) — file paths to policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: >
      An indexed repository structure (dict mapping (doc_name, section_number)
      to section title and body text).
    error_handling: >
      If any file is missing or unreadable, report error and exit with code 1.
      Ensure all numbered clauses are accurately indexed without truncation.

  - name: answer_question
    description: >
      Searches the indexed policy repository for the single section that directly
      governs the user's question. Generates an evidence-backed answer citing
      the document name and section number. If no document section explicitly
      covers the topic, emits the exact required refusal template.
    input: >
      question (str) — the employee's query.
      indexed_docs (dict) — the indexed document collection from retrieve_documents.
    output: >
      A string containing either:
      (1) A single-source answer with document name and section citation, or
      (2) The verbatim repository refusal template identifying the appropriate
      department to contact.
    error_handling: >
      If the question references multiple domains (e.g. personal phone + remote work),
      enforce single-source answering (e.g. IT section 3.1) and reject cross-document
      blending. Never output hedging language or general knowledge assertions.
