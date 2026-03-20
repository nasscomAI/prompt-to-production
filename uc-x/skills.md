# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number, reporting null or missing sections before returning.
    input: File paths (str) to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: An indexed structure mapping document name and section number to their text content, plus a count of any missing or unreadable sections.
    error_handling: If any file is missing or unreadable, report which file failed and continue with the remaining documents. Never silently skip a file.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to the user's question and returns it with a citation, or returns the refusal template if not covered.
    input: The user's question (str) and the indexed document structure from retrieve_documents.
    output: A response containing either the answer with source document name and section number, or the exact refusal template if the question is not covered in any document.
    error_handling: If the question matches content in more than one document and blending would be required, output the refusal template rather than combining sources.
