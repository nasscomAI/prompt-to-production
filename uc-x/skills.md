# skills.md — UC-X Policy Q&A Agent

skills:
  - name: retrieve_documents
    description: Simultaneously loads and indexes all three CMC policy documents (HR, IT, Finance) by their section numbers and document titles.
    input: Paths to the three policy .txt files.
    output: A searchable index of policy clauses mapped to their respective documents and sections.
    error_handling: Fail if any of the three core policy files are missing or unreadable.

  - name: answer_question
    description: Performs a high-precision search of the indexed documents to find the single most relevant source for a user's question, returning a cited answer or the mandatory refusal template.
    input: User question and the indexed policy data.
    output: A cited, single-source response OR the exact mandatory refusal template.
    error_handling: If multiple sources conflict or if the answer is partially present, prioritize the most restrictive policy or use the refusal template to avoid blending.
