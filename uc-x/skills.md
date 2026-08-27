# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Load all 3 policy .txt files, parse them into sections and clauses,
      and index them by document name and section number for fast lookup.
    input: >
      A directory path (string) containing the three policy .txt files:
      policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      A dictionary keyed by document filename, where each value is a
      list of section dicts containing section_number, section_title,
      and clauses (list of clause_number + clause_text).
    error_handling: >
      If any of the three files is missing, report which file is missing
      and continue with the available files. If a file cannot be parsed,
      report the error and skip that file.

  - name: answer_question
    description: >
      Search the indexed documents for relevant sections, then produce
      a single-source answer with citations, or the refusal template
      if the question is not covered.
    input: >
      The question string and the indexed documents (from
      retrieve_documents).
    output: >
      A string containing either: (a) the answer citing one source
      document and specific section numbers, or (b) the exact refusal
      template if no document covers the question.
    error_handling: >
      If the question matches sections in multiple documents and
      creates genuine ambiguity, answer from the most directly
      relevant single document with a note that other documents
      may touch on related topics. Never blend answers from
      multiple documents.
