
skills:
  - name: retrieve_documents
    description: Loads and indexes all authorized policy text files, splitting them into manageable sections identified by document name and clause numbers.
    input: List of file paths.
    output: A searchable index of policy sections.
    error_handling: Logs an error if any of the mandatory policy files are missing.

  - name: answer_question
    description: Performs a single-source search against the policy index to find the most relevant section that answers the user's query without blending sources or hallucinating details.
    input: User question (string) and indexed policy data.
    output: A factual answer with specific citations [Doc, Section] OR the official refusal template.
    error_handling: Triggers the refusal template if the confidence score for a direct answer is low or if no relevant section is found.