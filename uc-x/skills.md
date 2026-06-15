skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: No arguments; reads policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt from the data/policy-documents directory relative to the project root.
    output: Dict mapping each document filename (str) to a list of (section_id, section_text) tuples representing every parsed section.
    error_handling: Raises FileNotFoundError with the missing file path if any policy file cannot be found on disk.

  - name: answer_question
    description: Searches indexed policy documents for a single-source answer and returns it with document name + section citation, or the exact refusal template when no coverage exists.
    input: query (str) — natural-language question; index (dict) — output of retrieve_documents.
    output: Formatted string with relevant section text and citation ("Source: <doc> — Sections <n>"), or the exact refusal template when the question is not covered or scores below the relevance threshold.
    error_handling: Returns the refusal template when no section scores above the minimum relevance threshold, when the query yields no meaningful tokens, or when coverage is absent from all three documents.
