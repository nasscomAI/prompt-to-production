# skills.md — UC-X: Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files, parses them into structured sections
      indexed by document name and section number for fast lookup.
    input: >
      Directory path (string) containing the three policy .txt files:
      policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      A dictionary with document names as keys, each containing a dict of
      section_number -> section_text. Also returns metadata (reference,
      version, effective date) for each document.
    error_handling: >
      If any policy file is missing, raise FileNotFoundError with the
      missing file name. If a file has no parseable sections, log a
      warning and include the document with an empty sections dict.

  - name: answer_question
    description: >
      Searches indexed documents for the answer to a question, returns
      a single-source answer with citation or the refusal template.
    input: >
      The structured documents dictionary (output of retrieve_documents)
      and a question string.
    output: >
      A dictionary with keys: answer (string), source_document (string),
      source_section (string), is_refusal (boolean).
    error_handling: >
      If the question is empty, return the refusal template. If no
      document contains relevant information, return the refusal template.
      Never return a blended answer.
