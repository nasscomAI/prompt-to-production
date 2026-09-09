# skills.md — UC-X Multi-Document Policy Assistant

skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy text files by filename and section/clause number.
    input: List or dict of document paths (HR leave, IT acceptable use, Finance reimbursement).
    output: Structured index mapping (document_name, section_number) to section title and full text.
    error_handling: Verifies all three required policy files exist; raises FileNotFoundError if any file is missing.

  - name: answer_question
    description: Matches user inquiry against indexed policy sections and returns a single-source verified answer with citation or the exact refusal template.
    input: Question string and indexed policy documents from retrieve_documents.
    output: String response containing single-source factual answer with [document_name, section] citation, or the standard refusal template.
    error_handling: Rejects cross-document synthesis; forbids hedging phrases; outputs standard refusal template whenever no single section answers the query directly.
