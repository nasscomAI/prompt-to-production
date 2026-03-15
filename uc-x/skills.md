# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number, making them available for downstream lookup.
    input: List of file paths (strings) — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: An in-memory index mapping (document_name, section_number) → section_text, ready for querying.
    error_handling: If a file is missing or unreadable, raise a FileNotFoundError with the specific file name and halt — do not proceed with a partial index.

  - name: answer_question
    description: Searches the indexed policy documents for a single-source answer to the user's question and returns it with a citation, or returns the refusal template if no answer is found.
    input: A natural-language question string and the document index produced by retrieve_documents.
    output: Either (a) a single-source answer string with citation in the format "Source: <document_name>, section <section_number>", or (b) the exact refusal template string when the question is not covered.
    error_handling: If the question matches content from more than one document, do not blend — return the refusal template. If the index is empty or not loaded, raise an error and prompt the user to run retrieve_documents first.
