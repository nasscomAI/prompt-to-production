# skills.md — UC-X Policy Q&A Agent

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files, indexes them by document name and section
      number, and returns a structured dict for searching.
    input: >
      List of file paths: policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt
    output: >
      dict[str, dict] — keys are short document names ("HR Leave",
      "IT Acceptable Use", "Finance Reimbursement"), values are dicts with
      document metadata and a list of {section, text} entries.
    error_handling: >
      If a file cannot be read or parsed, log a warning and continue with
      the remaining documents. Never raise an exception.

  - name: answer_question
    description: >
      Takes a question string and the indexed documents, finds the single
      best-matching section from one document, and returns an answer with
      citation OR the refusal template if no match is found.
    input: >
      question (str), indexed_docs (dict from retrieve_documents)
    output: >
      dict with keys: answer (str), document (str or None), section (str
      or None), is_refusal (bool)
    error_handling: >
      If multiple documents have equally strong matches, refuse with the
      refusal template rather than blending. Return is_refusal=True when
      the question cannot be answered from any single source.
