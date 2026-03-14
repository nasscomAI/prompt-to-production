# skills.md

skills:
  - name: retrieve_documents
    description: Safely loads the designated policy documents (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`) and strictly indexes their text by document filename and section number to allow for verifiable citation.
    input: The file paths to the three policy documents.
    output: A structured index or dictionary linking specific chunks of text directly to their document name and section ID.
    error_handling: System panics and halts if any of the three required policy documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents for explicit answers, strictly rejecting cross-document synthesis and refusing unanswerable questions.
    input: The user's question string and the output of retrieve_documents.
    output: A precise response string explicitly citing the source document and section, or the verbatim refusal template.
    error_handling: Triggers the exact refusal template ("This question is not covered in the available policy documents...") if an answer requires blending across documents or relies on external "common practice" knowledge.
