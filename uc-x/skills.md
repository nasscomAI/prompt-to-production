# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all 3 policy files from disk, parses each into structured
      sections and clauses indexed by document name and section number.
      Returns a searchable index that allows looking up any clause by
      document and section reference.
    input: >
      A directory path (string) containing the 3 policy .txt files:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
    output: >
      A dictionary keyed by document filename, where each value is a list
      of section objects containing:
        - section_number (str): e.g. "3"
        - section_title (str): e.g. "PERSONAL DEVICES (BYOD)"
        - clauses (list[dict]): each with clause_id and full text
      The index supports keyword search across all documents and returns
      matching clauses with their document source and section reference.
    error_handling: >
      If any file is missing, print a warning but continue with available
      files. If no files can be loaded, print an error and exit.

  - name: answer_question
    description: >
      Takes a user question and the document index from retrieve_documents.
      Searches for relevant clauses, determines if the answer exists in
      exactly one document, and returns either a cited answer or the exact
      refusal template.
    input: >
      - question (str): the user's natural language question
      - doc_index (dict): the indexed documents from retrieve_documents
    output: >
      One of two formats:
        (a) ANSWER: A factual response citing one source document and
            section number, preserving all conditions and prohibitions.
            Format: "According to [document], Section [X.Y]: [answer]"
        (b) REFUSAL: The exact refusal template text if the question is
            not covered or would require cross-document blending.
    error_handling: >
      If the question is ambiguous, ask the user to clarify rather than
      guessing. If multiple sections in the SAME document are relevant,
      cite all of them. If sections from DIFFERENT documents are relevant,
      answer from the single most relevant document only, or refuse if
      blending would be required.
