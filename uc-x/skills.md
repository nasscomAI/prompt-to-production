skills:
  - name: retrieve_documents
    description: Loads the three company policy text files and parses them into a searchable index partitioned by filename and section number.
    input:
      type: file paths
      format: List of strings pointing to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output:
      type: structured index
      format: A collection of document objects containing section headings, section numbers, and associated text content.
    error_handling:
      - If any of the mandatory policy files are missing or unreadable, the skill must halt and report the specific file error.
      - If a document contains non-parsable section numbers, it should log a warning but continue indexing with available metadata.

  - name: answer_question
    description: Searches the indexed policy documents for a specific answer and returns a single-source response with citations or the mandatory refusal template.
    input:
      type: natural language question
      format: String query from the user (e.g., "Can I carry forward unused annual leave?").
    output:
      type: cited response or refusal
      format: String containing the answer plus "[Document Name] Section [Number]" OR the verbatim refusal template.
    error_handling:
      - If the answer requires information from more than one document, the skill must refuse to blend them and instead return the refusal template or the most restrictive single-source answer.
      - If the information is not found in any document, the skill must return the verbatim refusal template.
      - If the generated answer includes hedging phrases like "typically" or "generally", the skill must block the output and trigger a re-search or refusal.
