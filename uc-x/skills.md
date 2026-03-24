skills:
  - name: retrieve_documents
    description: Ingests and indexes the three core policy files, maintaining a mapping of content to specific section numbers and filenames.
    input: Directory path containing the .txt policy files.
    output: A structured index or searchable knowledge base partitioned by document source.
    error_handling: If any of the three mandatory files are missing, the system must fail to initialize and alert the user.

  - name: answer_question
    description: Performs a high-precision search across the indexed documents to find a single-source answer.
    input: User query string.
    output: A response string containing the direct answer + citation OR the verbatim refusal template.
    error_handling: If the search returns results from multiple documents that contradict or "blend," the skill must prioritize the IT policy for device/tech questions and the HR policy for conduct questions, never merging the two.