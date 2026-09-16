# skills.md — UC-X Ask My Documents Skills

retrieve_documents:
  description: >
    Load all three supplied policy documents and index their content by
    document name and section number.

  input:
    - policy_hr_leave.txt
    - policy_it_acceptable_use.txt
    - policy_finance_reimbursement.txt

  output:
    - indexed documents
    - document names
    - section numbers
    - section text

  rules:
    - "Load only the three supplied policy documents."
    - "Keep each document separate and preserve its section numbers."
    - "Never merge sections from different documents into a single source."
    - "Do not add external information or assumptions."

answer_question:
  description: >
    Search the indexed policy documents for the user's question and return
    an answer supported by one source document and section citation, or the
    exact refusal template when the question is not covered.

  input:
    - user question
    - indexed documents

  output:
    - single-source answer with document name and section citation
    - or exact refusal template

  rules:
    - "Use one source document for each factual answer."
    - "Never combine claims from different documents."
    - "Preserve every relevant condition, limit, approval requirement, exclusion, and time period."
    - "Cite the source document name and section number for every factual claim."
    - "Never use hedging phrases such as 'while not explicitly covered', 'typically', 'generally understood', or 'it is common practice'."
    - "If the question is not covered, return the exact refusal template without variations."
    - "Do not infer permission from related statements in another document."
