# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy text files and indexes them by document name and section number.
    input: File paths to the three policy documents: `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`.
    output: An indexed structure mapping document names to section IDs and text.
    error_handling: If any file is missing, unreadable, or cannot be parsed, return a clear error and stop.

  - name: answer_question
    description: Searches the indexed policy documents and returns either a single-source answer with citation or the exact refusal template.
    input: A user question string and the indexed document structure.
    output: A single answer string with document and section citation, or the exact refusal template.
    error_handling: If the question matches multiple documents ambiguously, refuse rather than blend; if no relevant section is found, return the exact refusal template.
