# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, parses them into structured sections indexed by document name and section number.
    input: >
      A directory path containing the three policy files:
      policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      A dictionary mapping (document_name, section_number) to section_text.
      Example: { ("policy_hr_leave.txt", "2.6"): "Employees may carry forward..." }
    error_handling: >
      If any of the three files is missing, raise an error listing which files
      are missing. If a file cannot be parsed into sections, warn and include
      the raw text under a single section "UNPARSED".

  - name: answer_question
    description: Searches indexed documents for relevant sections, returns a single-source answer with citation OR the refusal template.
    input: >
      A user question string and the indexed document dictionary from
      retrieve_documents.
    output: >
      Either: a single-source answer citing document name + section number
      for every factual claim, OR the exact refusal template if the question
      is not covered in any document.
    error_handling: >
      If the question matches sections in multiple documents, answer from the
      most directly relevant single document only. If no single document
      provides a clear answer, use the refusal template. Never blend, never
      hedge, never guess.
