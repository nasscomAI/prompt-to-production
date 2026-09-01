# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes content by document name and section number for single-source lookup.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt (UTF-8).
    output: Dict keyed by (document_name, section_id) e.g., ("policy_hr_leave.txt","2.6") → verbatim section text; plus flat index.
    error_handling: If any file missing → FileNotFoundError with path; if no sections parsed → ValueError; preserves exact section text for citation.

  - name: answer_question
    description: Searches indexed documents for single best matching section, returns single-source answer with citation or exact refusal template.
    input: Question string.
    output: String either "Answer: <verbatim text> Source: <doc> Section <id>" OR exact refusal template "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: If no single-source match above threshold → return refusal template exactly; never hedge, never blend two documents; always cite doc+section when answering.
