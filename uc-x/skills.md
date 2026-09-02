# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy .txt files and index them by document name and section number for single-source lookup.
    input: >
      A fixed list of three file paths: policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      An index mapping (document_name, section_number) -> section_text, preserving
      the source wording of each section exactly. Section numbers are the dotted
      identifiers found in the documents (e.g. 2.3, 3.1, 5.2).
    error_handling: >
      If any of the three files is missing or unreadable, raise a clear error
      before answering begins rather than answering from a partial index. Lines
      that do not belong to a numbered section are attached to the nearest
      preceding section and never invented.

  - name: answer_question
    description: Answer a user question from a single document section with a citation, or return the fixed refusal template.
    input: >
      question (str) from the user, plus the index built by retrieve_documents.
    output: >
      Either a single-source answer string ending with a citation of the form
      "<document_name>, section <number>" (exactly one document, one section), or
      the verbatim refusal template. Never returns content spanning two documents.
    error_handling: >
      Scores sections and selects the single best-matching section from one
      document. If no section scores above the relevance threshold, or if the best
      matches are genuinely ambiguous across two documents, it returns the refusal
      template verbatim instead of guessing or blending. It never emits hedging
      phrases and never merges two sections into one answer. All conditions of the
      chosen section are preserved; nothing outside that section's text is added.
