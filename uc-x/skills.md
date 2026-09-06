skills:
  - name: retrieve_documents
    description: Ingests the three municipal policy documents (HR Leave, IT Acceptable Use, Finance Reimbursement) and builds a structured section-level index.
    input: List of file paths to the policy text documents.
    output: Dict mapping document filenames to structured section records including section number, title, and body text.
    error_handling: Verifies file existence for all three documents; raises FileNotFoundError if any policy document is missing or unreadable.

  - name: answer_question
    description: Resolves an employee inquiry by querying the indexed policies, selecting the single authoritative source document, and returning cited guidance or the standard refusal template.
    input: User query string and the indexed policy document repository.
    output: Dict containing the answer string, cited document filename, cited section number, and a boolean flag indicating if the query was refused.
    error_handling: Refuses answers when the query attempts cross-document synthesis or is ungrounded; prohibits hedging expressions and outputs the exact refusal template when documents do not contain the answer.
