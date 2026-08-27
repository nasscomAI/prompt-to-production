skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy files by document name and section number for deterministic policy lookup.
    input: "Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
    output: "Structured index keyed by filename and section id, with normalized section text and retrievable metadata."
    error_handling: "If any required file is missing or cannot be parsed into numbered sections, return a hard validation error listing missing/unreadable file(s) and do not continue to Q&A."

  - name: answer_question
    description: Answers a user question from a single document source with explicit section citation, or returns the exact refusal template when coverage is absent/ambiguous.
    input: "User question string plus indexed policy sections from retrieve_documents."
    output: "Either (a) single-source answer with citation format '<filename> section <x.y>' for each claim, or (b) exact refusal template text."
    error_handling: "If evidence spans multiple documents, is ambiguous, or lacks direct section support, return the refusal template exactly. Reject hedging language and do not emit uncited claims."