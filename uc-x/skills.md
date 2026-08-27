# skills.md

skills: - name: retrieve_documents

    description: >
      Loads all company policy documents and indexes them by
      document name and section number for accurate retrieval.

    input: >
      Folder containing:
      - policy_hr_leave.txt
      - policy_it_acceptable_use.txt
      - policy_finance_reimbursement.txt

    output: >
      A structured dictionary indexed by document name and
      section number.

    error_handling: >
      If any document is missing or unreadable, return an error
      and stop processing without guessing.

-   name: answer_question

    description: \> Searches the indexed policy documents and answers
    the user's question using exactly one policy document whenever
    possible.

    input: \> User question (string) and indexed policy documents.

    output: \> Either:

    -   A single-source answer with:
        -   exact policy statement
        -   document name
        -   section number

    OR

    -   The required refusal template if the answer is unavailable,
        ambiguous, or would require combining information from multiple
        documents.

    error_handling: \> Never infer missing information. Never combine
    information across documents. Never use external knowledge. If no
    valid single-source answer exists, return the refusal template
    exactly as specified in the project requirements.
