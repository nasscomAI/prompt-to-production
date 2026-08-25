skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: >
      base_path (string, optional) — directory containing policy files, default "../data/policy-documents".
      Files expected: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      Indexed dict structure: { "policy_hr_leave.txt": { "2.6": "Employees may carry forward...", ... }, ... }
      Each document maps clause_id → clause_text (full text, whitespace collapsed). Also returns metadata per document
      (reference, version, effective date). Preserves clause order.
    error_handling: >
      If any file missing → raise FileNotFoundError listing missing file(s). If no clauses parsed → raise ValueError.
      Decorative separators and headers ignored. Never synthesizes content.

  - name: answer_question
    description: Searches indexed documents and returns single-source answer with citation OR refusal template.
    input: >
      question (string) — employee natural language question. index (dict from retrieve_documents).
    output: >
      String answer: either (a) factual answer citing exactly ONE source document and section number(s) (e.g., "Source: policy_hr_leave.txt Section 2.6"),
      with verbatim or near-verbatim obligation preserved, or (b) exact refusal template when not covered:
      "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
      No hedging phrases, no cross-document blending.
    error_handling: >
      If question empty/blank → return refusal template. If search finds matches in two different documents → pick the single best
      match (highest keyword overlap) OR refuse if ambiguity would require blending — never combine. If hedging phrases would be needed
      → refuse instead. All factual claims must include "Source: <doc> Section <num>" citation; if citation missing → treat as failure and refuse.
