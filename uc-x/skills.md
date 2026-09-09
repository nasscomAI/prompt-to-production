skills:
  - name: retrieve_documents
    description: >
      Loads all three policy documents and indexes their contents by document
      name and section number.

    input:
      type: policy documents
      files:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt

    output:
      type: document index
      fields:
        - document_name
        - section_number
        - section_text

    rules:
      - "Keep each document separate."
      - "Never merge sections from different documents."
      - "Preserve document names and section numbers."
      - "Do not add information that is not present in the source documents."

  - name: answer_question
    description: >
      Searches the indexed policy documents for an answer and returns a
      single-source answer with document and section citation, or the exact
      refusal template when the question is not covered.

    input:
      type: natural-language question

    output:
      type: answer
      format: >
        Answer grounded in one policy document with document name and section
        number citation, or the exact refusal template.

    rules:
      - "Select one source document for each factual answer."
      - "Never blend claims from multiple documents."
      - "Cite the source document name and section number."
      - "Do not infer permissions or obligations."
      - "Do not use hedging language."
      - "Use the exact refusal template when no supported answer exists."