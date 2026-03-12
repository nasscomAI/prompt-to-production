# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads the specific HR leave, IT acceptable use, and Finance reimbursement 
      policy .txt files. Parses the files into structured text blocks indexed 
      by Document Name and Section Number.
    input: >
      None. Hardcoded paths relative to the application: 
      ../data/policy-documents/policy_hr_leave.txt
      ../data/policy-documents/policy_it_acceptable_use.txt
      ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A combined list of dictionaries containing keys: 
      file_name, section_id, and section_text.

  - name: answer_question
    description: >
      Takes an arbitrary query and checks the indexed sections. Enforces the 
      agents.md rules strictly. To avoid the LLM blending trap entirely, 
      this maps specific keywords of questions to single sections.
    input: >
      query (str): The user's question.
      documents (list of dict): Indexed policy sections.
    output: >
      A carefully constructed string embodying either the specific answer 
      with mandatory `[Source: File, Section x.y]` citation, or the exact
      Refusal Template.
    enforcement:
      - "Refuse explicitly if query maps to multiple files to prevent blending."
      - "Output the exact refusal template character-for-character if concept not found."
      - "Never preface the response or hedge."
