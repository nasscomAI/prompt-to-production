# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: Base directory path (string) containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: An index dict mapping document filename to an ordered dict of section number to section text.
    error_handling: Raises FileNotFoundError naming the missing file if any of the three documents is absent. Never substitutes another document or invented text.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source cited answer or the exact refusal template.
    input: A user question (string) plus the document index from retrieve_documents.
    output: An answer string that either states facts from exactly one document with [filename §X.Y] citations, or the verbatim refusal template when no document covers the question.
    error_handling: On ambiguous cross-document matches returns the single highest-scoring document's answer (or the refusal template if answering would require blending). Never returns hedging phrases, never cites a section that does not exist, never blends two documents.
