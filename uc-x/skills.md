# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for searchable retrieval.
    input: A list of file paths to the three policy documents — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: An indexed document store where each entry has document_name, section_number, section_title, and full section text. Maintains clear boundaries between documents — no merging of content across files.
    error_handling: If any file is missing or empty, reports which file failed and continues indexing the remaining files. Never silently skips a document. If a file has no parseable sections, flags it as unparseable and excludes it from the index.

  - name: answer_question
    description: Searches the indexed documents for the most relevant section to answer a user question, returning a single-source answer with citation or the refusal template.
    input: A user question (string) and the indexed document store from retrieve_documents.
    output: Either (a) an answer citing exactly one document and section in the format "[document_name, Section X.X]", preserving all conditions, limits, and restrictions from the source, OR (b) the refusal template verbatim — "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: If the question matches content in multiple documents, answers from the single most directly relevant document only — never blends. If the combination creates genuine ambiguity, uses the refusal template. Never uses hedging phrases ("while not explicitly covered", "typically", "generally"). If the document store is empty or not loaded, refuses and asks user to load documents first.
