# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy (.txt) files and indexes them by document
      name and section number for lookup.
    input: >
      List of file paths: policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      A dictionary keyed by document name, where each value is a list of
      section objects with keys: section_number, heading, content.
    error_handling: >
      If any file is missing or unreadable, raise a FileNotFoundError
      listing which file could not be loaded. Do not proceed with partial
      data.

  - name: answer_question
    description: >
      Given a user question, searches the indexed documents for a relevant
      answer and returns a single-source response with citation or the
      refusal template.
    input: >
      A question string and the indexed document dictionary from
      retrieve_documents.
    output: >
      A string answer that either (a) cites one document + section number
      with the factual answer, or (b) returns the exact refusal template
      if no match is found.
    error_handling: >
      If the question matches content in multiple documents, return the
      answer from the most specific match in a single document — do not
      blend. If no match found, return the refusal template verbatim.
