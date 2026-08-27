# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for efficient lookup.
    input: >
      Directory path containing the three policy .txt files (policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: >
      A structured index mapping each document name to its sections, where each
      section contains: section_number, heading, and list of clauses with their
      full text. Enables lookup by document + section number.
    error_handling: >
      If any of the three expected files is missing, print a warning listing which
      files are available and which are missing. Proceed with available files but
      note the limitation in responses.

  - name: answer_question
    description: Searches the indexed documents for the answer to a user question and returns a single-source answer with citation, or the refusal template.
    input: >
      A natural language question string from the user.
    output: >
      Either: (a) A factual answer citing one document name and section number,
      using only information from that single source, OR (b) The exact refusal
      template if the question is not covered in any document.
    error_handling: >
      If the question is ambiguous or could be answered by blending multiple
      documents, answer from the single most relevant source only. If no single
      source provides a clear answer, use the refusal template. Never guess or
      hedge.
