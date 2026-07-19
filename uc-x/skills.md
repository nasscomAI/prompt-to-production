skills:
  - name: retrieve_documents
    description: >
      Load all three policy .txt files and index their content by document name
      and section number, preserving section headings and clause text.
    input: >
      list of strings — file paths to policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      dict — keys are document filenames (e.g. "policy_hr_leave.txt"), each
      value is a dict with "sections" (section_number → heading + clauses).
    error_handling: >
      If any file cannot be read or is empty, raise a clear error listing which
      file failed. If a document has no numbered sections, store it under a
      single section "0" with the raw text.

  - name: answer_question
    description: >
      Search the indexed documents for the user's question and return a single-
      source answer with citation, or the refusal template if the question is
      not covered.
    input: >
      query — string, the user's natural language question. documents — dict
      from retrieve_documents.
    output: >
      string — either a cited answer from one document (with document name and
      section number) or the verbatim refusal template. Never blends across
      documents.
    error_handling: >
      If no matching content is found in any document, return the refusal
      template verbatim. If multiple documents match, return the answer from
      the most specific match in a single document — never blend. If the query
      is empty, ask the user to rephrase.
