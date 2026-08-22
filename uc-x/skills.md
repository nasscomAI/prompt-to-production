# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy documents from disk and builds an index
      keyed by document filename and section number for fast lookup.
    input: >
      A list of strings: file_paths — the paths to the three policy .txt files
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Order does not matter.
    output: >
      A dict (the index) with structure:
        { "<filename>": { "<section_number>": "<section_text>", ... }, ... }
      e.g. { "policy_hr_leave.txt": { "2.3": "Employees must submit ...", ... } }
      All three documents are always indexed. Missing or unreadable files raise
      an error — a partial index is never returned.
    error_handling: >
      If any file in file_paths does not exist or cannot be read, raise
      FileNotFoundError listing the missing file. If a file contains no
      parseable numbered sections, raise ValueError("<filename>: no sections
      found"). Never return a partial index.

  - name: answer_question
    description: >
      Searches the document index for the section most relevant to the question
      and returns a single-source answer with a citation, or the exact refusal
      template if no document answers the question.
    input: >
      Two parameters:
        index    (dict as returned by retrieve_documents),
        question (string — the employee's natural-language question).
    output: >
      A dict with keys:
        answer   (string — the answer text or the exact refusal template),
        source   (string — "<filename>, section X.Y" or "NONE" if refused),
        refused  (bool — True if the refusal template was used, False otherwise).
      The refusal template text (used verbatim when refused=True):
        "This question is not covered in the available policy documents
        (policy_hr_leave.txt, policy_it_acceptable_use.txt,
        policy_finance_reimbursement.txt). Please contact [relevant team]
        for guidance."
    error_handling: >
      If the index is empty or missing required document keys, raise ValueError
      listing which documents are absent. If the question string is empty or
      None, return the refusal template with refused=True and source="NONE".
      Never raise an exception for an unanswerable question — return the refusal
      dict instead. Never combine text from two different document entries into
      a single answer field.
