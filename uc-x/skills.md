# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: list of file paths to policy documents (e.g., policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: structured object mapping document names and section numbers to section text.
    error_handling: raises error if any file is missing or unreadable; skips and flags sections that cannot be parsed; if a document is empty or unparseable, returns partial index and error message.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation or the refusal template if not found.
    input: question string and indexed documents structure from retrieve_documents.
    output: answer string with exact source document and section citation, or the refusal template verbatim if not found.
    error_handling: if answer would require blending multiple documents, returns refusal template; if question is ambiguous or not covered, returns refusal template; never uses hedging phrases or unsupported claims.

