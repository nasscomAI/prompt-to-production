skills:

* name: retrieve_documents
  description: Loads all three policy documents and indexes their numbered sections by document name and section number.
  input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
  output: Structured policy sections indexed by document filename and section number.
  error_handling: Reports missing or unreadable policy files instead of silently producing incomplete results.

* name: answer_question
  description: Answers a policy question using one source document and section, or returns the exact refusal template when the question is not covered.
  input: A natural-language policy question and the indexed policy documents.
  output: A single-source answer with document name and section citation, or the exact required refusal template.
  error_handling: Never blends documents, never uses unsupported assumptions or hedging, and preserves all conditions and prohibitions from the selected source.
