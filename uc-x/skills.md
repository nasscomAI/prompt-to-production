# skills.md — UC-X Ask My Documents
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: >
      Reads all three policy text files from hard-coded paths, extracts
      each section heading and subsection content, and indexes them by
      document file name and section number for fast lookup.
    input: >
      Three hard-coded file paths to policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: >
      A dict keyed by document file name, where each value is an ordered
      list of parsed sections, each containing section_number, title,
      and full body text.
    error_handling: >
      If a file is missing or unreadable, raise FileNotFoundError with
      the missing path. If a section cannot be parsed (no section number
      pattern), log a warning but continue loading the rest of the file.

  - name: answer_question
    description: >
      Given a user question and the indexed document structure, finds the
      single best-matching section by keyword overlap scoring. Returns
      an answer with citation (document name + section number) or the
      exact refusal template. Refuses if matches span multiple documents
      or if the best match score is below the threshold.
    input: >
      A question string and the document index dict from
      retrieve_documents.
    output: >
      A string: either (a) a cited answer formatted as "Per {doc_name},
      Section {section_number}: {policy_text}" or (b) the verbatim
      refusal template.
    error_handling: >
      If the question is empty, return the refusal template. If the
      question matches multiple documents with overlapping scores,
      refuse rather than blend.
