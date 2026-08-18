# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Load all three policy documents from disk and index them by document name
      and section number, returning a searchable structure for downstream skills.
    input: >
      doc_paths (list of strings): paths to the three policy files in this order:
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A dict keyed by document filename (e.g. "policy_hr_leave.txt"), where each
      value is a list of dicts with: section_number (string), section_title
      (string), and clause_text (string verbatim from the document). Sections are
      in document order.
    error_handling: >
      If any of the three files is missing or unreadable, raise FileNotFoundError
      naming the missing file and stop — do not return a partial index with some
      documents missing, as this would cause silent single-source violations.
      If a section cannot be parsed into a numbered clause, include it with
      section_number set to null so answer_question can detect and skip it.

  - name: answer_question
    description: >
      Search the indexed documents for an answer to the employee question and
      return a single-source cited answer or the exact refusal template.
    input: >
      question (string): the employee's free-text policy question.
      index (dict): the output of retrieve_documents — keyed by document filename,
      each value is a list of section dicts.
    output: >
      A dict with keys:
      - answer (string): either the answer text (with inline citation in the
        format "(Source: [filename], Section [number])") or the exact refusal
        template text if no document contains the answer.
      - source_doc (string or None): the filename of the single document the
        answer came from. None if the refusal template was issued.
      - source_section (string or None): the section number cited. None if refused.
      - refused (bool): True if the refusal template was issued, False otherwise.
    error_handling: >
      If the question matches sections in more than one document and combining
      them would be required to answer, do not blend — set refused: True and
      return the exact refusal template:
        "This question is not covered in the available policy documents
        (policy_hr_leave.txt, policy_it_acceptable_use.txt,
        policy_finance_reimbursement.txt). Please contact [relevant team]
        for guidance."
      If the question contains hedging-prone phrasing ("generally", "typically",
      "usually") that would require inferring beyond document text, refuse.
      Never return an answer that contains the phrases "while not explicitly
      covered", "typically", "generally understood", "it is common practice",
      or "it may be assumed".
