# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Load all three policy .txt files and index them by document name and
      section number for single-source lookup.
    input: >
      A list of UTF-8 policy file paths (default:
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt).
    output: >
      A structured index: for each document, metadata (document_name /
      filename) plus an ordered list of sections, each with section_id
      (e.g. "3.1") and exact section text. The index must keep documents
      separate so callers can retrieve by document name + section number
      without merging content across files.
    error_handling: >
      If any file is missing, unreadable, or empty, raise a clear error
      naming the path and do not invent policy text. If a file has no
      numbered sections (N.N pattern), raise a format error rather than
      fabricating structure. Never silently drop a section during parse,
      and never merge sections from different documents into one entry.

  - name: answer_question
    description: >
      Search the indexed policies for a single-source answer with citation,
      or return the refusal template when the question is not covered.
    input: >
      The structured index from retrieve_documents, plus the employee
      question as a plain string.
    output: >
      Either (1) a plain-text answer drawn from exactly one document, with
      every factual claim citing document name + section number, or (2) the
      exact refusal template: This question is not covered in the available
      policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Please contact [relevant team] for
      guidance. Cross-document trap questions (e.g. personal phone for work
      files from home) must answer from IT section 3.1 only or refuse —
      never blend with HR remote-work language.
    error_handling: >
      If the index is empty or malformed, refuse with a clear error — do not
      invent answers. If no section covers the question, or if answering
      would require combining two documents or using hedging language,
      return the refusal template exactly (no variations). Never cite two
      documents in one answer. Prefer a single governing section; if IT+HR
      (or any pair) create genuine ambiguity about permission, refuse rather
      than blend.
