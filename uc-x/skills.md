# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files, parses them into sections indexed by
      document name and section number, and returns a searchable index.
    input: >
      List of file paths (strings):
        - "../data/policy-documents/policy_hr_leave.txt"
        - "../data/policy-documents/policy_it_acceptable_use.txt"
        - "../data/policy-documents/policy_finance_reimbursement.txt"
    output: >
      Dict keyed by document filename, each value being a list of section
      objects:
        - section_id  (string, e.g. "3.1", "5.2")
        - heading     (string)
        - body        (string, exact clause text unmodified)
      All three documents must load successfully before the Q&A loop starts.
    error_handling: >
      If any file is missing or unreadable, print an error and exit:
        "LOAD_FAILED: <filename> could not be read. All documents required."
      Never start the Q&A loop with partial document coverage — a missing
      document would cause silent refusal failures.

  - name: answer_question
    description: >
      Searches the indexed documents for a single-source answer to the user's
      question and returns a cited answer or the exact refusal template.
    input: >
      - question  (string) — user's natural-language question
      - index     (dict)   — output of retrieve_documents
    output: >
      One of two string formats:
        A) Cited answer:
             "<answer text>
              Source: <filename>, section <X.Y>"
        B) Refusal template (verbatim, no variations):
             "This question is not covered in the available policy documents
              (policy_hr_leave.txt, policy_it_acceptable_use.txt,
              policy_finance_reimbursement.txt).
              Please contact [relevant team] for guidance."
      Never returns a blended answer citing two documents.
    error_handling: >
      If the question string is empty or fewer than 3 words, return:
        "Please enter a complete question."
      If the index is empty or missing, return the refusal template —
      do not attempt to answer from memory or general knowledge.
