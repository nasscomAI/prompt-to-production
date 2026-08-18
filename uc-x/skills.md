skills:

  retrieve_documents:
    description: >
      Loads all three CMC policy documents and indexes their content
      by document name and section number.

    input:
      - policy_hr_leave.txt
      - policy_it_acceptable_use.txt
      - policy_finance_reimbursement.txt

    output:
      - indexed_documents

    rules:
      - Keep each policy document separate.
      - Preserve document names and section numbers.
      - Never merge sections from different documents into one source.
      - Use only the supplied policy documents.

  answer_question:
    description: >
      Searches the indexed policy documents and returns an answer
      supported by a single source document and section citation, or
      returns the exact refusal template when the question is not
      covered.

    input:
      - indexed_documents
      - user_question

    output:
      - answer
      - source_document
      - section_number

    rules:
      - Never combine claims from different policy documents.
      - Every factual claim must include its document name and section number.
      - Never use outside knowledge or assumptions.
      - Never use hedging language to fill gaps.
      - If the question is not covered, return the exact refusal template.
      - If answering requires information from multiple documents, refuse rather than blend them.