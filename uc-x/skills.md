# skills.md — UC-X: Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy documents from disk, parses them into
      structured sections indexed by document filename and section number,
      and stores the indexed content in memory for search.
    input: >
      File paths (list of strings):
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A dictionary keyed by document filename, where each value is a
      dictionary of section numbers to section text. Example:
        {"policy_hr_leave.txt": {"2.6": "Employees may carry forward..."}}
    error_handling: >
      If any file is missing or unreadable, raise an error and report
      the missing filename. Do not silently skip documents — all three
      must be loaded successfully or the system must not start.

  - name: answer_question
    description: >
      Accepts a user question, searches the indexed policy documents for
      relevant sections, and returns a single-source answer with citation
      or the refusal template.
    input: >
      A natural-language question string from the user (e.g., "Can I carry
      forward unused annual leave?").
    output: >
      One of two formats:
        1. A factual answer drawn from exactly one document, with every
           claim citing the source document filename and section number.
           All conditions, limits, exceptions, and deadlines from the
           cited section must be included.
        2. The refusal template verbatim: "This question is not covered
           in the available policy documents (policy_hr_leave.txt,
           policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
           Please contact [relevant team] for guidance."
    error_handling: >
      If the question spans multiple documents (cross-document blending
      risk), answer from the single most directly relevant document only,
      or return the refusal template. Never combine claims from two
      documents. Never use hedging phrases such as "while not explicitly
      covered", "typically", or "it is common practice". If relevance
      is ambiguous, refuse rather than guess.
