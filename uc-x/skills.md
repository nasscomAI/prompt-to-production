# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes them by document name and section number for fast lookup during question answering.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed document store mapping document name and section number to clause text content.
    error_handling: If any policy file cannot be read or is missing expected section numbering, halt and report which file failed — do not proceed with partial document coverage.

  - name: answer_question
    description: Searches the indexed documents for relevant content to a user question, returns a single-source answer with citation, or returns the refusal template if no document covers the question.
    input: A natural language question string from the interactive CLI.
    output: Either (a) an answer text with source document name and section number cited, or (b) the exact refusal template if the question is not covered.
    error_handling: If the search returns content from multiple documents that could answer the question, select the single most relevant source — never blend. If no relevant content is found, output the refusal template — never guess or hedge.
