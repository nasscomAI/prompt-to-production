# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Load all three policy .txt files and index their content by document
      name and section number for efficient lookup.
    input: >
      A list of file paths (strings) pointing to the three policy documents.
    output: >
      An indexed structure mapping each document name to its parsed sections.
      Each section has: document_name, section_number, section_heading, and
      section_text. The index supports keyword search across all sections.
    error_handling: >
      If any file cannot be found or read, report which file failed and
      continue loading the remaining documents. If no files can be loaded,
      refuse to answer any questions and report the error.

  - name: answer_question
    description: >
      Search the indexed documents for sections relevant to the user's
      question, and return a single-source answer with citation or the
      refusal template.
    input: >
      A user question (string) and the indexed document structure from
      retrieve_documents.
    output: >
      One of two responses:
        1. An answer citing a specific document and section number (e.g.
           "According to policy_it_acceptable_use.txt, Section 3.1: ...").
           All conditions from the source clause must be preserved.
        2. The refusal template: "This question is not covered in the
           available policy documents (policy_hr_leave.txt,
           policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
           Please contact [relevant team] for guidance."
    error_handling: >
      If multiple documents contain relevant sections, present each
      document's answer separately with its own citation — never blend
      them into a combined statement. If the question is ambiguous, ask
      the user to clarify rather than guessing. Never use hedging phrases.
