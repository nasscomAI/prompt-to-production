# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy files and index them by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: A list of entries, each with document name, section number, section title, and the full
      verbatim section text (wrapped lines rejoined).
    error_handling: Raises a clear error if a file is missing or cannot be parsed; never silently
      drops a section from the index.

  - name: answer_question
    description: Search the indexed documents for the single section that best matches the question and
      return a verbatim, cited answer, or the refusal template if nothing matches.
    input: A question string and the indexed entries from retrieve_documents.
    output: Either "[<document> section <X.Y>]" followed by the section text quoted verbatim, or the
      exact refusal template when no section matches above the confidence threshold.
    error_handling: Never blends two documents into one answer; if the best match is below the
      confidence threshold it returns the refusal template instead of guessing; refuses rather than
      hedge when coverage is ambiguous.
