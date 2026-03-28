skills:
  - name: retrieve_documents
    description: Load and index the three approved policy documents for search.
    input: >
      File paths to the policy documents:
      policy_hr_leave.txt,
      policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt
    output: >
      A structured index of the documents containing document name,
      section numbers, and text content.
    error_handling: >
      If any document cannot be loaded or is missing, return an error
      message identifying the missing file and do not continue answering
      questions.

  - name: answer_question
    description: Search the indexed policy documents and return an answer based on a single document with citation.
    input: >
      A user question in plain text and the indexed policy documents.
    output: >
      A response containing the policy answer along with the source
      document name and section number. If the question is not covered,
      return the refusal template exactly.
    error_handling: >
      If the question matches multiple documents or creates ambiguity,
      refuse using the refusal template instead of combining information.