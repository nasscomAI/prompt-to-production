# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes policy clauses by document name and section number.
    input: Directory containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Dictionary keyed by document name, where each value is a list of section records containing section number and text.
    error_handling: Refuses to continue if any required policy document is missing.

  - name: answer_question
    description: Searches indexed policy documents and returns a single-source answer with citations, or the exact refusal template.
    input: User question string and indexed documents from retrieve_documents.
    output: Answer text containing source document name and section number for every factual claim, or the required refusal template.
    error_handling: Refuses when no section supports the question, when top evidence is ambiguous across documents, or when an answer would require combining claims from multiple documents.
